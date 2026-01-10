import sqlite3
from datetime import datetime

DB_FILE = "snutz.db"

def get_connection():
    """ Opens connection to DB """
    print("Connecting to db...")
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection

def init_database():
    """ Creates the database tables if they don't exist """
    print("initializing database...")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'offline',
            last_seen TEXT,
            registered_at TEXT NOT NULL        
            
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database Initialized")
    
def register_device(device_id: str, name: str):
    """ Add a new device to the database """
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT OR REPLACE INTO devices
        (device_id, name, status, last_seen, registered_at)
        VALUES (?, ?, ?, ?, ?)
    """, (device_id, name, "online", now, now))
    
    conn.commit()
    conn.close()
    
    return{
        "device_id": device_id,
        "name": "name",
        "status": "online",
        "registered_at": now
    }
    
def get_all_devices():
    """ Gets all devices from the database """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM devices")
    rows = cursor.fetchall()
    
    devices = []
    for row in rows:
        devices.append(dict(row))
    
    conn.close()
    return devices
   
def update_heartbeat(device_id: str):
    """ Updates last_seen timestamp for a device """
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # UPDATE timestamp and status online
    cursor.execute("""
        UPDATE devices
        SET LAST_SEEN = ?, status = 'online'
        WHERE device_id = ?               
    """, (now, device_id))
    
    if cursor.rowcount == 0:
        conn.close()
        return None # no device found
    
    conn.commit()
    conn.close()
    
    return {"last_seen": now, "status": "online"}
        
    
#Test code
if __name__ == "__main__":
    print("Testing DB..")
    init_database()
    
    # Test adding device
    print("\nRegistering a device...")
    result = register_device("test-1", "Test Device")
    print(f"Result: {result}")
    
    # Test getting all devices
    print("\nGetting all devices..")
    devices = get_all_devices()
    print(f"Found{len(devices)} device(s):")
    for device in devices:
        print(f" = {device}")
        
    print("\n Tests Done!")