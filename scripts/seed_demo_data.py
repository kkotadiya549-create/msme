import os
import sys
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent dir to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_db, get_db
from models.machine import Machine
from models.sensor_reading import SensorReading
from models.ticket import Ticket

async def seed():
    load_dotenv()
    
    if not os.environ.get("MONGODB_URI"):
        print("No MONGODB_URI found, skipping seed script.")
        return
        
    connect_db()
    db = get_db()
    if db is None:
        print("Could not connect to db.")
        return
        
    print("Connected to MongoDB. Clearing old demo data...")
    await db["machines"].delete_many({})
    await db["sensorreadings"].delete_many({})
    await db["tickets"].delete_many({})
    await db["messages"].delete_many({})
    await db["digests"].delete_many({})
    
    print("Seeding Machines...")
    machines = [
        Machine(machineId="1", metric="temperature", normalRangeMin=20, normalRangeMax=60),
        Machine(machineId="2", metric="noise", normalRangeMin=30, normalRangeMax=85),
        Machine(machineId="3", metric="temperature", normalRangeMin=15, normalRangeMax=45)
    ]
    await db["machines"].insert_many([m.model_dump(by_alias=True, exclude_none=True) for m in machines])
    
    print("Seeding historical Sensor Readings...")
    now = datetime.now()
    readings = [
        SensorReading(machineId="1", metric="temperature", value=40, timestamp=now - timedelta(hours=2)),
        SensorReading(machineId="2", metric="noise", value=50, timestamp=now - timedelta(hours=1)),
        SensorReading(machineId="3", metric="temperature", value=90, timestamp=now - timedelta(minutes=10)) # Abnormal
    ]
    await db["sensorreadings"].insert_many([r.model_dump(by_alias=True, exclude_none=True) for r in readings])
    
    print("Seeding Tickets...")
    tickets = [
        Ticket(machineId="3", actionType="maintenance_ticket", priority="high", reasoning="Sensor data confirms abnormal reading for physical issue.", status="open", createdAt=now - timedelta(minutes=9)),
        Ticket(machineId="1", actionType="inventory_alert", priority="medium", reasoning="Operational issue reported.", status="resolved", createdAt=now - timedelta(hours=24))
    ]
    await db["tickets"].insert_many([t.model_dump(by_alias=True, exclude_none=True) for t in tickets])
    
    print("Seed complete! Ready for demo.")

if __name__ == "__main__":
    asyncio.run(seed())
