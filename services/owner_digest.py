import os
from datetime import datetime
import httpx
from database import get_db
from models import Digest

async def build_and_send_digest():
    try:
        db = get_db()
        if db is None:
            return
            
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        message_count = await db["messages"].count_documents({
            "timestamp": {"$gte": start_of_day, "$lte": end_of_day}
        })
        
        cursor = db["tickets"].find({
            "createdAt": {"$gte": start_of_day, "$lte": end_of_day}
        })
        tickets = await cursor.to_list(length=1000)
        
        summary_text = f"Today: {message_count} messages processed."
        
        if len(tickets) == 0:
            summary_text += " No other issues."
        else:
            maintenance_tickets = [t for t in tickets if t.get("actionType") == "maintenance_ticket"]
            inventory_alerts = [t for t in tickets if t.get("actionType") == "inventory_alert"]
            
            if maintenance_tickets:
                summary_text += f" {len(maintenance_tickets)} maintenance tickets."
                for t in maintenance_tickets:
                    summary_text += f" ({t.get('priority')} priority - Machine {t.get('machineId')}, {t.get('status')})."
                    
            if inventory_alerts:
                summary_text += f" {len(inventory_alerts)} inventory alerts."
                for t in inventory_alerts:
                    summary_text += f" ({t.get('priority')} priority - Machine {t.get('machineId')}, {t.get('status')})."
                    
        digest_date = now.date().isoformat()
        
        digest = Digest(
            date=digest_date,
            content=summary_text,
            sentAt=now
        )
        await db["digests"].insert_one(digest.model_dump(by_alias=True, exclude_none=True))
        
        token = os.environ.get("WHATSAPP_TOKEN")
        phone_number_id = os.environ.get("FROM_PHONE_NUMBER_ID")
        owner_number = os.environ.get("OWNER_PHONE_NUMBER")
        
        if owner_number and token and phone_number_id:
            url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": owner_number,
                "type": "text",
                "text": {"body": summary_text}
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
            print("Owner digest sent successfully.")
        else:
            print("OWNER_PHONE_NUMBER not set or config missing. Digest saved to DB only.")
            
    except Exception as e:
        print(f"Error generating owner digest: {e}")
