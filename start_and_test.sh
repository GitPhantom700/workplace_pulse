export PYTHONHTTPSVERIFY=0
.venv/bin/uvicorn main:app --port 8081 &
SERVER_PID=$!
sleep 5
curl -s -X POST http://127.0.0.1:8081/api/scenarios/seed -H "Content-Type: application/json" -d '{"scenario_id": "hardware_lifecycle"}' > out.json
kill $SERVER_PID
cat out.json
