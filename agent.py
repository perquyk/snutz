import requests
import time

#configuration
DEVICE_ID = "test-1"
DEVICE_NAME = "Test"
SERVER_URL = "http://0.0.0.0:8000"

print(f"Starting agent: {DEVICE_ID} ({DEVICE_ID}) on server {SERVER_URL}")

# Register with the server
response = requests.post(
    f"{SERVER_URL}/devices/register",
    params={
        "device_id": DEVICE_ID,
        "name": DEVICE_NAME
    }
)

print(f"Registration response: {response.json()}")

#Keep running
print("Agent is running. Press CTRL+C to stop.")
while True:
    time.sleep(10)
