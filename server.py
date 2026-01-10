from fastapi import FastAPI
from contextlib import asynccontextmanager
import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting sNutz server...")
    database.init_database()
    print("Server Ready!")
    yield
    
    # Shutdown
    print("sNutz server shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "Hello from SNUTZ!"}

@app.get("/devices")
def get_devices():
    devices = database.get_all_devices()
    return {"devices": devices}

@app.post("/devices/register")
def register_device(device_id: str, name: str):
    device = database.register_device(device_id, name)
    return {"message": "Device Registered!", "Device": device}

@app.post("/devices/{device_id}/heartbeat")
def hearbeat(device_id: str):
    """ Agent check if still online """
    result = database.update_heartbeat(device_id)
    
    if result is None:
        return {"error": "Device not found"}, 404
    
    return {
        "message": "Heartbeat received",
        "device_id": device_id,
        "last_seen": result["last_seen"]
    }
    
@app.post("/tests/results")
def submit_test_result(device_id: str, test_type: str, target: str, result_data: str, triggered_by: str = "manual"):
    """ Receives test result from agent """
    result = database.save_test_result(
        device_id,
        test_type,
        target,
        result_data,
        triggered_by
    )
    return{
        "message": "Test result saved",
        "result": result
    }
    
@app.get("/tests/results")
def get_test_resulst(device_id: str = None, limit: int = 50):
    """Gets test results (optional filter by deviceId) """
    results = database.get_test_results(device_id, limit)
    return {
        "count": len(results),
        "results": results
    }