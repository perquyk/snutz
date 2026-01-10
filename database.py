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
    
    # DEVICES TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'offline',
            last_seen TEXT,
            registered_at TEXT NOT NULL        
            
        )
    """)
    
    # TEST RESULT TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            test_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            target TEXT,
            result_data TEXT,
            triggered_by TEXT DEFAULT 'manual',
            FOREIGN KEY (device_id) REFERENCES devices (device_id)
        )
    """)
    
    # COMMANDS TABLE    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            command_type TEXT NOT NULL,
            parameters TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            completed_at TEXT,
            result_id INTEGER,
            FOREIGN KEY (device_id) REFERENCES devices (device_id),
            FOREIGN KEY (result_id) REFERENCES test_results (id)
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
   
def get_device(device_id: str):
    """ Gets ONE device from the database """   
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
    row = cursor.fetchone()
   
    conn.close()
    
    if row:
        return dict(row)
    else:
        return None
   
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
        
def save_test_result(device_id: str, test_type: str, target: str, result_data: str, triggered_by: str = "manual"):
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO test_results
        (device_id, test_type, timestamp, target, result_data, triggered_by) 
        VALUES (?, ?, ?, ?, ?, ?)               
    """, (device_id, test_type, now, target, result_data, triggered_by))
    
    result_id = cursor.lastrowid
    conn.commit()
    conn.close()
            
    return {
        "id": result_id,
        "device_id": device_id,
        "test_type": test_type,
        "timestamp": now,
        "target": target,
        "result_data": result_data
    } 
    
def get_test_results(device_id: str = None, limit: int = 50):
    """ Gets the test results from the db """
    conn = get_connection()
    cursor = conn.cursor()
    
    if device_id:
        #get results for a specific device
        cursor.execute("""
            SELECT * FROM test_results
            WHERE device_id =  ?
            ORDER BY timestamp DESC
            LIMIT ?               
        """, (device_id, limit))
    else:
        #get results for ALL devices
        cursor.execute("""
            SELECT * FROM test_results
            ORDER BY timestamp DESC
            LIMIT ?               
        """, (limit,))
    
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    
    conn.close()
    return results
    
def create_command(device_id: str, command_type: str, parameters: str = None):
    """ Creates a new command for a device """
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
         
    cursor.execute("""
        INSERT INTO commands
        (device_id, command_type, parameters, status, created_at)
        VALUES (?, ?, ?, 'pending', ?)
    """, (device_id, command_type, parameters, now))
    
    command_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return{
        "id": command_id,
        "device_id": device_id,
        "command_type": command_type,
        "parameters": parameters,
        "status": 'pending',
        "created_at": now
    }

def get_pending_commands(device_id: str):
    """ Gets all pending commands for a device """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM commands
        WHERE device_id = ? AND status = 'pending'
        ORDER BY created_at ASC
    """, (device_id,))
    
    rows = cursor.fetchall()
    commands = [dict(row) for row in rows]
    
    conn.close()
    return commands

def update_command_status(command_id: int, status: str, result_id: int = None):
    """ Updates a command's status """
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    if status == "completed":
        cursor.execute("""
            UPDATE commands
            SET status = ?, completed_at = ?, result_id = ?
            WHERE id = ?               
        """, (status, now, result_id, command_id))
    else:
        cursor.execute("""
            UPDATE commands
            SET status = ?
            WHERE id = ?    
        """, (status, command_id))

    conn.commit()
    conn.close()
    
    return {"id": command_id, "status": status}
         
def get_all_commands(device_id: str = None, limit: int = 50):
    """ Gets command s(optionally filtered by device)"""         
    conn = get_connection()
    cursor = conn.cursor()
    
    if device_id:
        cursor.execute("""
            SELECT * FROM commands
            WHERE device_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (device_id, limit))
    else:
        cursor.execute("""
            SELECT * FROM commands
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
    rows = cursor.fetchall()
    commands = [dict(row) for row in rows]
    
    conn.close()
    return commands
         
# TEST CODE
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