import os
import httpx

async def send_reply(to: str, text: str):
    token = os.environ.get("WHATSAPP_TOKEN")
    phone_number_id = os.environ.get("FROM_PHONE_NUMBER_ID")
    
    if not token or not phone_number_id:
        print("Missing WhatsApp config.")
        return
        
    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            print(f"Reply sent to {to}")
    except Exception as e:
        print(f"Failed to send reply: {e}")
