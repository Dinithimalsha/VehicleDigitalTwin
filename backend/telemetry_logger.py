import sqlite3
import json
import time

class TelemetryLogger:
    def __init__(self, db_name="telemetry.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                data TEXT
            )
        ''')
        self.conn.commit()

    def log(self, data):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO telemetry (timestamp, data) VALUES (?, ?)', 
                       (data.get('timestamp', time.time()), json.dumps(data)))
        self.conn.commit()

    def get_all_sessions(self):
        # In a real app, we would group by session ID
        pass

    def get_playback_data(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT data FROM telemetry ORDER BY timestamp ASC')
        rows = cursor.fetchall()
        return [json.loads(row[0]) for row in rows]

    def close(self):
        self.conn.close()
