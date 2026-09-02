from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
response = client.post("/api/scenarios/seed", json={"scenario_id": "hardware_lifecycle"})
data = response.json()
print("saas_metrics:", data.get('saas_metrics'))
print("saas_metrics length:", len(data.get('saas_metrics', [])))
