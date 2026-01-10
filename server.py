from fastapi import FastAPI

app = FastAPI()

#remporary database for start of development
devices = []

#todo Add html dashboard to endpoints.

@app.get("/")
def home():
    return {"message": "Hello from SNUTZ!"}

@app.get("/devices")
def get_devices():
    return {"devices": devices}

@app.post("/devices/register")
def register_device(device_id: str, name: str):
    #create new device
    new_device= {
        "device_id": device_id,
        "name": name
    }

    #add to list
    devices.append(new_device)
    return {"message": "Device Registered!", "Device": new_device}
