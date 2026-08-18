# SecureEV Factory Monitoring

SecureEV is a factory monitoring assistant with a FastAPI backend, a React dashboard, MongoDB persistence, WhatsApp webhook integration, and an agent pipeline for interpreting operational messages and sensor readings.

## Features

- WhatsApp webhook verification and inbound message handling
- Multi-agent message processing for operational issues
- MongoDB storage for messages, tickets, and sensor readings
- Ticket filtering and resolution from the React dashboard
- Sensor ingestion and latest-reading endpoints
- Scheduled owner digest delivery
- Demo data seeding and sensor simulation scripts

## Architecture

The Python backend in the repository root exposes the API and serves the application workflow. The `agents/` package coordinates message analysis, `models/` defines persisted data shapes, and `services/` handles WhatsApp and digest delivery. The React/Vite dashboard lives in `client/` and consumes the backend API. MongoDB stores application data.

## Technology Stack

- Python, FastAPI, Uvicorn, Pydantic
- Motor and MongoDB
- OpenAI API for agent-assisted analysis
- React, Vite, and Tailwind CSS
- Docker Compose for the application and MongoDB services

## Installation

Create and activate a virtual environment, then install backend dependencies:

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd client
npm install
```

## Environment Setup

Copy `.env.example` to `.env` and provide local values. Keep `.env` private. The backend requires `MONGODB_URI`, `WHATSAPP_TOKEN`, `FROM_PHONE_NUMBER_ID`, `VERIFY_TOKEN`, and `OPENAI_API_KEY`. Set `VITE_API_BASE_URL` only when the frontend API is not served from the same origin.

## Backend Startup

From the repository root:

```bash
uvicorn main:app --reload --port 3000
```

## Frontend Startup

From `client/`:

```bash
npm run dev
```

The Vite development server normally runs at `http://localhost:5173`.

## Charger Simulator Startup

The demo scripts simulate factory sensor activity and seed sample records:

```bash
python scripts/seed_demo_data.py
python scripts/simulate_sensor.py
```

Both scripts require a reachable MongoDB instance and the appropriate environment configuration.

## Testing

Run the Python test suite when tests are present:

```bash
pytest
```

Build and lint the frontend:

```bash
cd client
npm run build
npm run lint
```

## Security Features

- Environment-based configuration for credentials and API tokens
- Webhook verification token validation
- Input validation through Pydantic models
- No credentials or local runtime data should be committed

## Demo Instructions

1. Start MongoDB locally or with `docker compose up mongodb`.
2. Configure `.env` with the required demo values.
3. Start the backend and frontend using the commands above.
4. Seed demo data and run the sensor simulator.
5. Open the dashboard and review or resolve generated tickets.

For WhatsApp webhook testing, expose the backend with a secure tunnel such as ngrok and configure the callback URL and verification token in Meta Developer tools.
