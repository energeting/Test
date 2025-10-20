from locust import HttpUser, task, between
import random

class OpenBMCTest(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.auth = ("root", "OpenBmc")
    
    @task(2)
    def get_system_info(self):
        """Запрос информации о системе"""
        with self.client.get("/redfish/v1/Systems/system", 
                           auth=self.auth, 
                           verify=False, 
                           catch_response=True,
                           name="OpenBMC_SystemInfo") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(1)
    def get_power_state(self):
        """Запрос состояния питания"""
        with self.client.get("/redfish/v1/Systems/system", 
                           auth=self.auth, 
                           verify=False, 
                           catch_response=True,
                           name="OpenBMC_PowerState") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    power_state = data.get("PowerState", "Unknown")
                    response.success()
                except:
                    response.failure("Failed to parse JSON")
            else:
                response.failure(f"Status: {response.status_code}")

class PublicAPITest(HttpUser):
    wait_time = between(1, 5)
    
    @task(3)
    def get_posts(self):
        """Запрос списка постов из JSONPlaceholder"""
        with self.client.get("/posts", 
                           catch_response=True,
                           name="JSONPlaceholder_Posts") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(2)
    def get_comments(self):
        """Запрос комментариев"""
        with self.client.get("/comments", 
                           catch_response=True,
                           name="JSONPlaceholder_Comments") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(1)
    def get_weather(self):
        """Запрос погоды с wttr.in"""
        with self.client.get("/London?format=3", 
                           catch_response=True,
                           name="Weather_London") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
