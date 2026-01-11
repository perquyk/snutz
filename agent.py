import requests
import time
import json
from tests import ping_test, speedtest_test, traceroute_test

# Configuration
DEVICE_ID = "test-1"
DEVICE_NAME = "Test Device"
SERVER_URL = "http://0.0.0.0:8000"
HEARTBEAT_INTERVAL = 30
CHECK_COMMANDS_INTERVAL = 10  # Check for commands every 10 seconds

print(f"Starting agent: {DEVICE_ID} ({DEVICE_NAME})")
print(f"Server: {SERVER_URL}")

# Register with server
print("\nRegistering with server...")
response = requests.post(
    f"{SERVER_URL}/devices/register",
    params={"device_id": DEVICE_ID, "name": DEVICE_NAME}
)
print(f"Registered: {response.json()}")

# Main loop
print(f"\nHeartbeat every {HEARTBEAT_INTERVAL}s")
print(f"Checking for commands every {CHECK_COMMANDS_INTERVAL}s")
print("Press CTRL+C to stop.\n")

heartbeat_counter = 0
command_check_counter = 0

def execute_command(command):
    """Executes a command and returns the result"""
    command_id = command["id"]
    command_type = command["command_type"]
    parameters = command.get("parameters")
    
    print(f"\nExecuting command #{command_id}: {command_type}")
    
    # Parse parameters if they exist
    if parameters:
        params = json.loads(parameters)
    else:
        params = {}
    
    # Execute based on command type
    if command_type == "ping":
        target = params.get("target", "google.com")
        count = params.get("count", 4)
        
        print(f"   Pinging {target} ({count} packets)...")
        result = ping_test(target, count)
        
        # Save result to server
        response = requests.post(
            f"{SERVER_URL}/tests/results",
            params={
                "device_id": DEVICE_ID,
                "test_type": "ping",
                "target": target,
                "result_data": json.dumps(result),
                "triggered_by": "command"
            }
        )
        
        if response.status_code == 200:
            result_id = response.json()["result"]["id"]
            
            # Mark command as completed
            requests.post(
                f"{SERVER_URL}/commands/{command_id}/complete",
                params={"result_id": result_id, "status": "completed"}
            )
            
            if result["success"]:
                print(f"   Command completed! Result ID: {result_id}")
            else:
                print(f"   Ping failed but result saved")
        else:
            print(f"   Failed to save result")
    
    elif command_type == "speedtest":
      print("Running speedtest (This takes 30-60 secs)")
      result = speedtest_test()
      
      #Save result to server
      response = requests.post(
          f"{SERVER_URL}/tests/results",
          params={
              "device_id": DEVICE_ID,
              "test_type": "speedtest",
              "target": result.get("server_location", "N.A"),
              "result_data": json.dumps(result),
              "triggered_by": "command"
          }
      )
      
      if response.status_code == 200:
        result_id = response.json()["result"]["id"]
          
        requests.post(f"{SERVER_URL}/commands/{command_id}/complete",
                    params={"result_id": result_id, "status": "completed"}
        )
        
        if result["success"]:
            print(f"Speedtest Completed!")
            print(f"Download: {result['download_mbps']} Mbps")
            print(f"Upload: {result['upload_mbps']} Mbps")
            print(f"Ping: {result['ping_ms']} ms")
        else:
            print(f"Speedtest FAILED: {result.get('error')}")
    
    elif command_type == "traceroute":
        target = params.get("target", "google.com")
        max_hops = params.get("max_hops", 30)
        
        print(f"Tracing route to {target} (max {max_hops} hops)...")
        result = traceroute_test(target, max_hops)
        
        #Save result to server
        response = requests.post(f"{SERVER_URL}/tests/results",
            params={
                "device_id": DEVICE_ID,
                "test_type": "traceroute",
                "target": target,
                "result_data": json.dumps(result),
                "triggered_by": "command"
            }
        )
        
        if response.status_code == 200:
            result_id = response.json()["result"]["id"]
            
            requests.post(
                f"{SERVER_URL}/commands/{command_id}/complete",
                params={"result_id": result_id, "status": "completed"}
            )
            
            if result["success"]:
                print(f"Traceroute completed")
                print(f"hops: {result['hop_count']}")
                print(f"Reuslt ID: {result_id}")
            else:
                print(f"Traceroute FAILED: {result.get('error')}")
        else:
            print("Failed to save result")
    
    else:
        print(f"   Unknown command type: {command_type}")
        # Mark as failed
        requests.post(
            f"{SERVER_URL}/commands/{command_id}/complete",
            params={"status": "failed"}
        )

try:
    while True:
        # Send heartbeat
        if heartbeat_counter >= HEARTBEAT_INTERVAL:
            response = requests.post(f"{SERVER_URL}/devices/{DEVICE_ID}/heartbeat")
            if response.status_code == 200:
                print(f"Heartbeat sent")
            heartbeat_counter = 0
        
        # Check for commands
        if command_check_counter >= CHECK_COMMANDS_INTERVAL:
            response = requests.get(f"{SERVER_URL}/commands/pending/{DEVICE_ID}")
            
            if response.status_code == 200:
                data = response.json()
                if data["count"] > 0:
                    print(f"\nFound {data['count']} pending command(s)")
                    for command in data["commands"]:
                        execute_command(command)
            
            command_check_counter = 0
        
        # Wait 1 second
        time.sleep(1)
        heartbeat_counter += 1
        command_check_counter += 1
        
except KeyboardInterrupt:
    print("\n\nAgent stopped")