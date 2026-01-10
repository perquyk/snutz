import sqlite3
from datetime import datetime

DB_FILE = "snutz.db"

def get_connection():
    """ Opens connection to DB """
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection

def init_database():
    """ Creates the database tables if they don't exist """
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
    
    
    
    if __name__ == "__main__":
        print("Testing DB..")
        init_database()