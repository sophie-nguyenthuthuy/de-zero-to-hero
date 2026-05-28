"""
Locust Load Test — FastAPI DE Lab

Chạy: locust -f locustfile.py --host http://localhost:8000
Sau đó mở: http://localhost:8089
"""
from locust import HttpUser, between, task


class DEApiUser(HttpUser):
    wait_time = between(0.5, 2)   # Random wait 0.5-2s giữa các request

    def on_start(self):
        """Chạy khi user bắt đầu — lấy token"""
        response = self.client.post(
            "/auth/token",
            data={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(5)   # Weight 5 — request này xảy ra nhiều nhất
    def list_customers(self):
        self.client.get("/customers", headers=self.headers, name="/customers")

    @task(3)
    def get_customer(self):
        for cid in ["C001", "C002", "C003"]:
            self.client.get(
                f"/customers/{cid}", headers=self.headers, name="/customers/[id]"
            )

    @task(2)
    def monthly_revenue(self):
        self.client.get(
            "/analytics/revenue/monthly?year=2024", headers=self.headers
        )

    @task(1)
    def top_customers(self):
        self.client.get("/analytics/customers/top?limit=5", headers=self.headers)

    @task(1)
    def health_check(self):
        self.client.get("/health")


class ReadOnlyUser(HttpUser):
    """Simulate viewer users"""

    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.post(
            "/auth/token",
            data={"username": "viewer", "password": "viewer123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task
    def browse_analytics(self):
        self.client.get("/analytics/revenue/monthly", headers=self.headers)
