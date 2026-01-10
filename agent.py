import requests
import time
import json
from tests import ping_test

# Configuration
DEVICE_ID = "test-1"
DEVICE_NAME = "Test"
SERVER_URL = "http://0.0.0.0:8000"
HEARTBEAT_INTERVAL = 30 # SECONDS
TEST_INTERVAL = 60

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
print(f"Sending hearbeat every {HEARTBEAT_INTERVAL}s...")
print(f"Ping test every {TEST_INTERVAL}s...")
print("Press CTRL+C to stop.\n")

heartbeat_counter = 0
test_counter = 0

try:
    while True:
        # Send heartbeat every set interval (set in HEARTBEAT_INTERVAL)
        if heartbeat_counter >= HEARTBEAT_INTERVAL:
            response = requests.post(f"{SERVER_URL}/devices/{DEVICE_ID}/heartbeat")
            if response.status_code == 200:
                print("Heartbeat sent")
            heartbeat_counter = 0
        
        # Run ping test every set interval (set in TEST_INTERVAL)
        if test_counter >= TEST_INTERVAL:
            print("\nRunning ping test to google.com")
            result = ping_test("google.com", count=4)
            
            #Send result to server
            response = requests.post(
                f"{SERVER_URL}/tests/results",
                params={
                    "device_id": DEVICE_ID,
                    "test_type": "ping",
                    "target": "google.com",
                    "result_data": json.dumps(result),
                    "triggered_by": "cron"
                }
            )
            if response.status_code == 200:
                if result["success"]:
                    print(f"[PING] - [SUCCESS] - Results saved to server")
                else:
                    print(f"[PING] - [FAILED] - {result.get('error', "Unknown error")}")
            
            test_counter = 0
        
        #wait 1 second
        time.sleep(1)
        heartbeat_counter += 1
        test_counter += 1
            
except KeyboardInterrupt:
    print("\n\n Agent stopped by user.")
