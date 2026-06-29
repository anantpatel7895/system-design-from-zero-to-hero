import threading
import requests

from main import app

response = requests.get(
    "http://localhost:8080/hello"
)

assert response.status_code == 200