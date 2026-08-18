import sys
import os
import asyncio
import random
import time
from datetime import datetime
import httpx

async def send_reading(machine_id, metric, normal_min, normal_max, drift_probability, base_url):
    is_abnormal = random.random() < drift_probability
    
    if is_abnormal:
        too_high = random.random() > 0.5
        offset = random.random() * (normal_max - normal_min) * 0.5
        value = normal_max + offset if too_high else normal_min - offset
        print(f"[ABNORMAL] Generating drifted value: {value:.2f}")
    else:
        value = normal_min + random.random() * (normal_max - normal_min)
        print(f"[NORMAL] Generating valid value: {value:.2f}")
        
    try:
        url = f"{base_url}/sensors/reading"
        payload = {
            "machineId": machine_id,
            "metric": metric,
            "value": round(value, 2),
            "timestamp": datetime.now().isoformat()
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            print(f"Reading sent successfully to machine {machine_id}.")
    except Exception as e:
        print(f"Failed to send reading: {e}")

async def main():
    args = sys.argv[1:]
    if len(args) < 4:
        print("Usage: python simulate_sensor.py <machineId> <metric> <normalMin> <normalMax> [driftProbability]")
        sys.exit(1)
        
    machine_id = args[0]
    metric = args[1]
    normal_min = float(args[2])
    normal_max = float(args[3])
    drift_probability = float(args[4]) if len(args) > 4 else 0.1
    
    base_url = os.environ.get("API_BASE_URL", "http://localhost:3000")
    
    print(f"Starting simulator for Machine {machine_id} ({metric}). Normal range: [{normal_min}, {normal_max}]. Drift probability: {drift_probability * 100}%")
    print("Sending reading every 30 seconds... (Press Ctrl+C to stop)")
    
    while True:
        await send_reading(machine_id, metric, normal_min, normal_max, drift_probability, base_url)
        await asyncio.sleep(30)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Simulator stopped.")
