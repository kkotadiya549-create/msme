import os
# pyrefly: ignore [missing-import]
import uvicorn
from contextlib import asynccontextmanager
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Request, HTTPException, status
# pyrefly: ignore [missing-import]
from fastapi.responses import PlainTextResponse, FileResponse
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# pyrefly: ignore [missing-import]
from apscheduler.triggers.cron import CronTrigger
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from bson import ObjectId
# pyrefly: ignore [missing-import]
from pymongo import ReturnDocument

from database import connect_db, get_db
from orchestrator import run_pipeline
from services.owner_digest import build_and_send_digest
from services.whatsapp_service import send_reply
from models.message import Message
from models.sensor_reading import SensorReading
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Load env variables
load_dotenv()

# Validate env vars
required_env_vars = [
    'MONGODB_URI', 'WHATSAPP_TOKEN', 'FROM_PHONE_NUMBER_ID',
    'VERIFY_TOKEN', 'OPENAI_API_KEY'
]
missing = [var for var in required_env_vars if not os.environ.get(var)]
if missing:
    print('CRITICAL STARTUP ERROR: The following environment variables are missing:')
    for var in missing:
        print(f" - {var}")
    print('Please configure them in your .env file before starting the server.')
    exit(1)

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    connect_db()
    print("MongoDB connected")
    
    cron_schedule = os.environ.get('DIGEST_CRON_SCHEDULE', '0 18 * * *').strip('"\'')
    # APScheduler uses a different format, but we can parse simple cron expressions
    parts = cron_schedule.split()
    if len(parts) == 5:
        minute, hour, day, month, day_of_week = parts
        scheduler.add_job(
            build_and_send_digest,
            CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week),
            id='daily_digest'
        )
    scheduler.start()
    print("Scheduled daily owner digest")
    
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Webhook Routes
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode and token:
        if mode == "subscribe" and token == os.environ.get("VERIFY_TOKEN"):
            print("WEBHOOK_VERIFIED")
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        raise HTTPException(status_code=400, detail="Bad Request")

@app.post("/webhook")
async def receive_webhook(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    if body.get("object") == "whatsapp_business_account":
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                if messages:
                    msg = messages[0]
                    sender_number = msg.get("from")
                    message_type = msg.get("type")
                    message_text = msg.get("text", {}).get("body", "") if message_type == "text" else ""
                    timestamp = datetime.fromtimestamp(int(msg.get("timestamp")))
                    
                    print(f"Received message from {sender_number}: {message_text}")
                    
                    # Save to MongoDB
                    db = get_db()
                    if db is not None:
                        new_message = Message(
                            senderNumber=sender_number,
                            messageText=message_text,
                            messageType=message_type,
                            timestamp=timestamp
                        )
                        await db["messages"].insert_one(new_message.model_dump(by_alias=True, exclude_none=True))
                        
                    # Run Multi-Agent Pipeline
                    pipeline_result = await run_pipeline(message_text)
                    
                    # Send dynamic reply
                    reply_text = pipeline_result.get("replyText", "Got it, noted.")
                    await send_reply(sender_number, reply_text)
        return PlainTextResponse(content="OK", status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Not Found")

# Tickets Routes
class TicketPatch(BaseModel):
    status: str

@app.get("/tickets")
async def get_tickets(status: Optional[str] = None, priority: Optional[str] = None):  # noqa: A002
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="DB not connected")
        
    filter_query = {}
    if status:
        filter_query["status"] = status
    if priority:
        filter_query["priority"] = priority
        
    cursor = db["tickets"].find(filter_query).sort("createdAt", -1)
    tickets = await cursor.to_list(length=1000)
    
    # Convert _id to string for JSON serialization
    for t in tickets:
        t["_id"] = str(t["_id"])
        
    return tickets

@app.patch("/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, patch_data: TicketPatch):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="DB not connected")
        
    try:
        obj_id = ObjectId(ticket_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
        
    if patch_data.status not in ['resolved', 'in_progress', 'open']:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    result = await db["tickets"].find_one_and_update(
        {"_id": obj_id},
        {"$set": {"status": patch_data.status}},
        return_document=ReturnDocument.AFTER
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    result["_id"] = str(result["_id"])
    return result

# Status Route
@app.get("/status")
async def get_status():
    db = get_db()
    db_connected = db is not None
    last_message_at = None
    
    if db_connected:
        try:
            last_msg = await db["messages"].find_one({}, sort=[("timestamp", -1)])
            if last_msg:
                last_message_at = last_msg.get("timestamp")
        except Exception:
            pass
            
    return {
        "agentsOnline": True,
        "dbConnected": db_connected,
        "lastMessageAt": last_message_at
    }

# Sensors Routes
class ReadingInput(BaseModel):
    machineId: str = Field(min_length=1)
    metric: str = Field(min_length=1)
    value: float
    timestamp: Optional[datetime] = None

@app.post("/sensors/reading")
async def post_reading(reading: ReadingInput):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="DB not connected")
        
    ts = reading.timestamp or datetime.now()
    new_reading = SensorReading(
        machineId=reading.machineId,
        metric=reading.metric,
        value=reading.value,
        timestamp=ts
    )
    
    reading_dict = new_reading.model_dump(by_alias=True, exclude_none=True)
    result = await db["sensorreadings"].insert_one(reading_dict)
    reading_dict["_id"] = str(result.inserted_id)
    return reading_dict

@app.get("/sensors/{machine_id}/latest")
async def get_latest_reading(machine_id: str):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="DB not connected")
        
    reading = await db["sensorreadings"].find_one({"machineId": machine_id}, sort=[("timestamp", -1)])
    if not reading:
        raise HTTPException(status_code=404, detail="No sensor data found for this machine")
        
    reading["_id"] = str(reading["_id"])
    return reading

# Digest Route
@app.post("/digest/trigger")
async def trigger_digest():
    try:
        await build_and_send_digest()
        return {"success": True, "message": "Digest generated and sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve React App static assets
client_dist = os.path.join(os.path.dirname(__file__), "client", "dist")
if os.path.exists(client_dist):
    assets_dir = os.path.join(client_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Catch-all: serve React index.html for any unmatched route (must be last)
@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    # Skip if this matches known API prefixes
    api_prefixes = ("webhook", "tickets", "status", "sensors", "digest")
    if any(full_path.startswith(p) for p in api_prefixes):
        raise HTTPException(status_code=404, detail="Not Found")

    index_path = os.path.join(client_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Not Found")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
