from database import get_db

async def run(listening_data: dict) -> dict:
    machine_id = listening_data.get("machineId")
    if not machine_id:
        return {"correlationStatus": "no_machine_id"}
        
    try:
        db = get_db()
        if db is None:
            raise Exception("Database not connected")
            
        machine = await db["machines"].find_one({"machineId": machine_id})
        if not machine:
            return {"correlationStatus": "no_machine_found"}
            
        reading = await db["sensorreadings"].find_one(
            {"machineId": machine_id},
            sort=[("timestamp", -1)]
        )
        if not reading:
            return {"correlationStatus": "no_sensor_data"}
            
        value = reading.get("value")
        min_val = machine.get("normalRangeMin")
        max_val = machine.get("normalRangeMax")
        
        if value is None or min_val is None or max_val is None:
            return {"correlationStatus": "incomplete_data"}
        
        is_normal = min_val <= value <= max_val
        
        return {
            "correlationStatus": "normal" if is_normal else "abnormal",
            "latestReading": value,
            "metric": reading.get("metric")
        }
    except Exception as e:
        print(f"sensorCorrelationAgent failed: {e}")
        return {"correlationStatus": "error"}
