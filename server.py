from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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
    
@app.post("/commands/create")
def create_command(device_id: str, command_type: str, parameters: str = None):
    """ Creates a command for a device to execute """
    
    # Check if device exists
    device = database.get_device(device_id)
    if not device:
        return {"error": "Device not found"}, 404
    
    command = database.create_command(device_id, command_type, parameters)
    
    return {
        "message": "Command created",
        "command": command
    }

@app.post("/commands/{command_id}/complete")
def complete_command(command_id: int, result_id: int = None, status: str = "completed"):
    """Marks a command as completed"""
    result = database.update_command_status(command_id, status, result_id)
    return {
        "message": "Command updated",
        "result": result
    }
    
@app.get("/commands/pending/{device_id}")
def get_pending_commands(device_id: str):
    """ Agents checks for pending commands """
    commands = database.get_pending_commands(device_id)
    return {
        "count": len(commands),
        "commands": commands
    }
    
@app.get("/commands")
def get_all_commands(device_id: str = None, limit: int = 50):
    """ Views all commands """
    commands = database.get_all_commands(device_id, limit)
    return{
        "count": len(commands),
        "commands": commands
    }
    
@app.post("/schedules/create")
def create_schedule(
    device_id: str,
    test_type: str,
    interval_seconds: int,
    target: str = None,
    parameters: str = None
):
    """Creates a new test schedule"""
    #validate that device exists
    device = database.get_device(device_id)
    if not device:
        return {"error": "device not found"}, 404
    
    schedule = database.create_schedule(
        device_id, test_type, interval_seconds, target, parameters
    )
    
    return {
        "message": "Schedule Created",
        "schedule": schedule
    }
    
@app.get("/schedules")
def get_schedules(device_id: str = None, enabled_only: bool = False):
    """ Gets all schedules (optionally filtered) """
    schedules = database.get_schedules(device_id, enabled_only)
    return {
        "count": len(schedules),
        "schedules": schedules
    }
    
@app.get("/schedules/due/{device_id}")
def get_due_schedules(device_id: str):
    """Gets schedules that are due to run for this device"""
    schedules = database.get_schedules_due_to_run(device_id)
    return {
        "count": len(schedules),
        "schedules": schedules
    }
    
@app.post("/schedules/{schedule_id}/toggle")
def toggle_schedule(schedule_id: int, enabled: bool):
    """Enabled/Disable a schedule"""
    result = database.toggle_schedule(schedule_id, enabled)
    return {
        "message": "Schedule updated",
        "result": result
    }
    
@app.post("/schedules/{schedule_id}/ran")
def mark_schedule_ran(schedule_id: int):
    """Marks that a schedule just ran"""
    result = database.update_schedule_last_run(schedule_id)
    return {
        "message": "Schedule updated",
        "result": result
        
    }

@app.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: int):
    """Deletes a schedule"""
    result = database.delete_schedule(schedule_id)
    return {
        "message": "Schedule deleted",
        "result": result
    }
    
    