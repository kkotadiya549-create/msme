import os
import json
from openai import AsyncOpenAI

async def run(message_text: str) -> dict:
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
            
        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a factory monitoring assistant. Extract the following from the message:
1. machineId: The ID of the machine mentioned (e.g., "3" if "Machine 3"), or null.
2. issueType: One of: temperature, noise, stock, delay, other.
3. urgencyGuess: One of: low, medium, high.
4. summary: A one-line summary.
Respond ONLY with a JSON object. No markdown."""
                },
                {"role": "user", "content": message_text}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        parsed = json.loads(content)
        
        return {
            "machineId": parsed.get("machineId") or None,
            "issueType": parsed.get("issueType") or 'unclassified',
            "urgencyGuess": parsed.get("urgencyGuess") or 'low',
            "summary": parsed.get("summary") or 'No summary'
        }
    except Exception as e:
        print(f"listeningAgent failed: {e}")
        return {"issueType": "unclassified"}
