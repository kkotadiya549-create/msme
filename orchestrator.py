from agents import listening_agent, sensor_correlation_agent, maintenance_inventory_agent, coordinator_agent

async def run_pipeline(message_text: str) -> dict:
    try:
        # 1. Listen & Extract
        listening_data = await listening_agent.run(message_text)
        
        # 2. Correlate with Sensor Data
        sensor_data = await sensor_correlation_agent.run(listening_data)
        
        # 3. Decide Action
        action_data = maintenance_inventory_agent.run(listening_data, sensor_data)
        
        # 4. Coordinate Final Response & Create Ticket if needed
        final_result = await coordinator_agent.run(listening_data, sensor_data, action_data)
        
        return final_result
    except Exception as e:
        print(f"Orchestrator failed: {e}")
        return {"replyText": "Got it, noted."}
