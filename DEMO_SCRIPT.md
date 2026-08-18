# Live Demo Script

This script is designed for a seamless 5-minute hackathon presentation of the WhatsApp Factory Monitor.

## 0. Preparation (Before Demo)
1. Run `docker-compose up --build` or run locally (`npm start`).
2. Make sure the database is seeded. (The container runs the seed script automatically via `npm start`).
3. Set up ngrok and update your Webhook URL in the Meta Developer Console if testing live WhatsApp messages.
4. Open the dashboard at `http://localhost:3000`. Show that there is 1 open high-priority ticket (seeded data for Machine 3).

## 1. Scenario 1: The Ambiguous Message
**Goal**: Show how the LLM extracts intent and the orchestrator handles missing machine correlations.
- **Action**: From the test WhatsApp number, send: *"We are running out of spare bolts in the main warehouse."*
- **Result**: The agent parses this as a `stock` issue. Since no machine is specified, it doesn't query sensors. It creates an **Inventory Alert**.
- **Dashboard**: Refresh the dashboard to show the new Inventory Alert ticket.

## 2. Scenario 2: The Critical Machine Failure
**Goal**: Show sensor correlation logic.
- **Action**: In the background (or via a quick cURL/Postman), send a fake abnormal sensor reading:
  `curl -X POST http://localhost:3000/sensors/reading -H "Content-Type: application/json" -d '{"machineId":"1","metric":"temperature","value":105}'`
- **Action**: Send WhatsApp message: *"Machine 1 is vibrating a lot and feels really hot!"*
- **Result**: LLM parses `machineId: 1` and `issueType: temperature`. The Correlation Agent checks the latest reading (105) against normal ranges (20-60) and confirms it is **abnormal**. It creates a **Maintenance Ticket**.
- **WhatsApp Reply**: Show the audience the dynamic reply: *"Checked Machine 1's last reading (105), looks abnormal. Logged a maintenance ticket, priority: high."*

## 3. Resolving a Ticket
**Goal**: Show the supervisor's workflow.
- **Action**: In the dashboard, click **Mark Resolved** next to the newly created Machine 1 maintenance ticket.
- **Result**: The ticket status instantly updates to `resolved`, moving it out of the active high-priority counts.

## 4. Triggering the Owner Digest
**Goal**: Show the end-of-day summary without waiting for the cron job.
- **Action**: Send a POST request to trigger the digest:
  `curl -X POST http://localhost:3000/digest/trigger`
- **Result**: Check the WhatsApp account designated as the "owner". Show the summary message that aggregates the day's activity (the seeded tickets + the ones you just created).
