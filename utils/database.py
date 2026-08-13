import sqlite3
import pandas as pd
from datetime import datetime

DB_FILE = "emergencies.db"

def init_db():
    """Creates the database table if it doesn't already exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            title TEXT,
            category TEXT,
            district TEXT,
            safety_status TEXT,
            published TEXT,
            logged_at TEXT,
            url TEXT,
            UNIQUE(title, published)
        )
    ''')
    conn.commit()
    conn.close()

def log_incidents(incidents_list):
    """Saves new active incidents to the database, ignoring duplicates."""
    if not incidents_list:
        return
        
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for inc in incidents_list:
        c.execute('''
            INSERT OR IGNORE INTO history 
            (title, category, district, safety_status, published, logged_at, url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (inc['title'], inc['category'], inc['district'], inc['safety_status'], inc['timestamp'], current_time, inc['url']))
        
    conn.commit()
    conn.close()

def load_history():
    """Loads all historical data into a Pandas DataFrame."""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM history ORDER BY logged_at DESC", conn)
    conn.close()
    return df