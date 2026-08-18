# Migration Notes: Node.js to Python/FastAPI

## Overview
This document outlines the changes made to port the WhatsApp Factory Monitor backend from Node.js (Express + Mongoose) to Python (FastAPI + Motor + Pydantic). The architecture, route paths, and database schemas remain identical to ensure seamless integration with the existing React dashboard and WhatsApp webhooks.

## Key Changes

### Framework & Routing
- **Express.js → FastAPI**: `server.js` and the `src/routes/` directory were consolidated and translated into `main.py`. FastAPI provides modern asynchronous routing and built-in OpenAPI documentation.
- **Port**: The application runs on Port 3000 by default (configured in `main.py` via uvicorn) to match the previous Node.js server and avoid requiring changes to the React client's API base URL.

### Database Access & Models
- **Mongoose → Motor & Pydantic**: Mongoose schemas (`src/models/`) were replaced with Pydantic models (`models/`). 
  - The `MongoBaseModel` in `models/base.py` maps MongoDB's internal `_id` to `id` for JSON serialization, matching the structure expected by the frontend.
  - The async `motor` driver replaces Mongoose for database queries.

### Scheduled Jobs
- **node-cron → APScheduler**: The daily owner digest script was updated to use Python's `APScheduler`. The cron format and logic inside `services/owner_digest.py` mirrors the previous implementation.

### Agent Logic
- **Agents (`src/agents/` → `agents/`)**: 
  - `listeningAgent.js` was ported to `listening_agent.py` using the official Python `openai` library.
  - Rule-based agents (`maintenanceInventoryAgent.js`, `sensorCorrelationAgent.js`, `coordinatorAgent.js`) were mapped 1:1, preserving all decision-making logic and returned fields.

### Orchestrator
- **`src/orchestrator.js` → `orchestrator.py`**: The sequential execution and fallback mechanisms were preserved.

### Webhook & HTTP Clients
- **axios → httpx**: External HTTP requests to the WhatsApp Cloud API are now handled using `httpx` instead of `axios`.

### Scripts
- **`simulateSensor.js` → `simulate_sensor.py`**: Direct port utilizing `asyncio` and `httpx`.
- **`seedDemoData.js` → `seed_demo_data.py`**: Rewritten to use Motor and Pydantic models for inserting default demo data.

## Running the Python Backend

### Prerequisites
1. Ensure Python 3.9+ is installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure your `.env` file is configured with the following:
   ```env
   PORT=3000
   MONGODB_URI=mongodb://127.0.0.1:27017/whatsapp
   WHATSAPP_TOKEN=...
   FROM_PHONE_NUMBER_ID=...
   VERIFY_TOKEN=...
   OPENAI_API_KEY=...
   OWNER_PHONE_NUMBER=...
   DIGEST_CRON_SCHEDULE="0 18 * * *"
   ```

### Starting the Server
Run the FastAPI application via uvicorn:
```bash
uvicorn main:app --port 3000
```
*(Use `--reload` during development to auto-restart the server on file changes).*

### Seeding Data
Run the demo data seeder script:
```bash
python scripts/seed_demo_data.py
```

### Simulating Sensors
Run the sensor simulation script:
```bash
python scripts/simulate_sensor.py <machineId> <metric> <normalMin> <normalMax> [driftProbability]
```
