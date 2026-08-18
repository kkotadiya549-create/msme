# Pilot Testing Checklist

Welcome to the Factory Monitoring Assistant pilot phase! Use this guide to set up the environment, run simulations, and monitor system health.

## 1. Onboarding a New Machine
Before the system can detect abnormal readings, the machine's valid operating parameters must be defined in the database.
1. Connect to your MongoDB database (e.g., via MongoDB Compass).
2. Open the `machines` collection.
3. Insert a new document representing your machine:
   ```json
   {
     "machineId": "3",
     "metric": "temperature",
     "normalRangeMin": 20,
     "normalRangeMax": 80
   }
   ```

## 2. Onboarding a New Worker
No account creation or web app is necessary for floor workers.
1. Save the Meta Test WhatsApp Number into the worker's phone contacts (e.g., as "Factory Assistant").
2. Have the worker send a message to that number.
3. As long as the WhatsApp Cloud API webhook is active, their messages will route through the system.

## 3. Running the Sensor Simulator
To test the backend logic without real hardware, use the included sensor simulation script.

**Usage:**
```bash
node scripts/simulateSensor.js <machineId> <metric> <normalMin> <normalMax> [driftProbability]
```
**Example:**
```bash
node scripts/simulateSensor.js 3 temperature 20 80 0.15
```
This sends a temperature reading for Machine 3 every 30 seconds. 85% of the time it will be between 20 and 80. 15% of the time it will deliberately exceed those limits to trigger abnormal alerts during your testing.

## 4. Monitoring the Pilot
- **Status Checks**: Hit `GET http://localhost:3000/status` to ensure the DB and agents are online.
- **Audit Logs**: All requests are logged inside the `logs/` directory (e.g., `logs/access.log`), which rotates daily. You can inspect this file for detailed API traffic.
- **Owner Digest**: The digest automatically summarizes the day at 6 PM (configurable via `DIGEST_CRON_SCHEDULE`). Check your WhatsApp for the message, or look in the `digests` MongoDB collection.
- **Dashboard**: Run the local Vite app (`cd client && npm run dev`) to visually track active tickets.

## 5. Common Failure Points
If things stop working during testing, check these first:
1. **ngrok Tunnel Expired**: The free tier of ngrok changes URLs upon restart. If you restart ngrok, you *must* update the Webhook Callback URL in the Meta Developer Console.
2. **Meta Token Expired**: Temporary WhatsApp access tokens expire every 24 hours. Generate a new one in the Meta Developer Console and update `WHATSAPP_TOKEN` in your `.env` file. Restart the backend after updating.
3. **MongoDB Whitelist**: Ensure your current IP address is whitelisted in MongoDB Atlas.
