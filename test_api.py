import httpx

# Replace with your Railway app's public URL
BASE_URL = "https://north-langchain-langgraph-starter-production.up.railway.app"

def test_health_check():
    response = httpx.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_agent_run():
    payload = {"input": "Hello, agent!"}
    response = httpx.post(f"{BASE_URL}/agent/run", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success" 