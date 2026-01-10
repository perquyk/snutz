import requests
import time

# Configuration
DEVICE_ID = "test-1"
DEVICE_NAME = "Test"
SERVER_URL = "http://0.0.0.0:8000"
HEARTBEAT_INTERVAL = 30 # SECONDS

print(f"Starting agent: {DEVICE_ID} ({DEVICE_NAME})\nServer: {SERVER_URL}")

# 1: Register with the server
response = requests.post(
    f"{SERVER_URL}/devices/register",
    params={
        "device_id": DEVICE_ID,
        "name": DEVICE_NAME
    }
)
print(f"Registration response: {response.json()}")

# 2: Keep running and send heartbeats back to server
print(f"Sending hearbeat every {HEARTBEAT_INTERVAL} seconds...")
print("Press CTRL+C to stop.\n")

try:
    while True:
        # Send heartbeat
        response = requests.post(f"{SERVER_URL}/devices/{DEVICE_ID}/heartbeat")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Heartbeat sent @ {data['last_seen']}")
        else:
            print(f"Heartbeat failed: {response.status_code}")
            
        #wait before next heartbeat
        time.sleep(HEARTBEAT_INTERVAL)

except KeyboardInterrupt:
    print("\n\n Agent stopped by user.")
