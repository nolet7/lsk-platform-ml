"""Small typed client for the versioned ML/legacy simulator API."""
import httpx

class InspectionMLClient:
    def __init__(self, base_url="http://127.0.0.1:8765", key="local-demo-key"):
        self.client = httpx.Client(base_url=base_url, headers={"X-Demo-Key": key}, timeout=10)

    def repair_order(self, order_id: str) -> dict:
        response = self.client.get(f"/v1/repair-orders/{order_id}")
        response.raise_for_status()
        return response.json()

    def predict(self, inspection_id: str, signals: dict) -> dict:
        response = self.client.post("/v1/predictions", json={"inspection_id": inspection_id, "signals": signals})
        response.raise_for_status()
        return response.json()

    def close(self):
        self.client.close()
