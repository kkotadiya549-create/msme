from database import get_db
from models import Ticket

async def run(listening_data: dict, sensor_data: dict, action_data: dict) -> dict:
    machine_id = listening_data.get("machineId")
    summary = listening_data.get("summary")
    
    correlation_status = sensor_data.get("correlationStatus")
    latest_reading = sensor_data.get("latestReading")
    
    action_type = action_data.get("actionType")
    priority = action_data.get("priority")
    reasoning = action_data.get("reasoning")
    
    ticket_created = False
    
    try:
        if action_type in ['maintenance_ticket', 'inventory_alert'] and machine_id:
            ticket = Ticket(
                machineId=machine_id,
                actionType=action_type,
                priority=priority,
                reasoning=reasoning
            )
            db = get_db()
            if db is not None:
                await db["tickets"].insert_one(ticket.model_dump(by_alias=True, exclude_none=True))
                ticket_created = True
                
        reply_text = f"Noted. {summary or 'Received your message'}. "
        if machine_id:
            if correlation_status == 'abnormal':
                reply_text += f"Checked Machine {machine_id}'s last reading ({latest_reading}), looks abnormal. "
            elif correlation_status == 'normal':
                reply_text += f"Checked Machine {machine_id}'s last reading ({latest_reading}), looks normal. "
                
        if ticket_created:
            formatted_action = action_type.replace('_', ' ')
            reply_text += f"Logged a {formatted_action}, priority: {priority}."
            
        return {
            "replyText": reply_text.strip(),
            "actionType": action_type,
            "priority": priority,
            "ticketCreated": ticket_created
        }
    except Exception as e:
        print(f"coordinatorAgent failed: {e}")
        return {
            "replyText": "Got it, noted.",
            "actionType": "error",
            "priority": "low",
            "ticketCreated": False
        }
