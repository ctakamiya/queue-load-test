import time
from locust import HttpUser, task, between

class QuickstartUser(HttpUser):
    # Define the wait time between tasks (randomly between 1 and 5 seconds)
    wait_time = between(1, 5)

    # This method runs when a virtual user starts
    def on_start(self):
        # Simulate a login request
        self.client.post("/login", json={"username": "testuser", "password": "password"})

    # Define a task for the virtual user
    @task
    def browse_homepage(self):
        self.client.get("/home")

    # Define another task with a higher weight (executed more frequently)
    @task(3)
    def view_items(self):
        for item_id in range(5):  # Simulate browsing multiple items
            self.client.get(f"/item?id={item_id}", name="/item")
            time.sleep(1)  # Simulate user delay between requests

