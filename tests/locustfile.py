from locust import HttpUser, task, between
import time


class User(HttpUser):
    wait_time = between(1, 2)

    @task
    def index_page(self):
        self.client.get("/")

    @task(3)
    def see_restaurant_page(self):
        self.client.get("/restaurants")

    def on_start(self):
        pass
