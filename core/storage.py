import sqlite3
import os

class Storage:
    def __init__(self, db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT UNIQUE,
            hostname TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            device_ip TEXT,
            app TEXT,
            message TEXT,
            severity TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            device_ip TEXT,
            description TEXT,
            severity TEXT
        )""")
        self.conn.commit()

    def register_device(self, ip, hostname):
        self.conn.execute(
            "INSERT OR IGNORE INTO devices(ip, hostname) VALUES (?, ?)",
            (ip, hostname)
        )
        self.conn.commit()

    def insert_log(self, log):
        self.conn.execute(
            "INSERT INTO logs(timestamp, device_ip, app, message, severity) VALUES (?, ?, ?, ?, ?)",
            (log["timestamp"], log["source_ip"], log["app"], log["message"], log["severity"])
        )
        self.conn.commit()

    def insert_alert(self, alert):
        self.conn.execute(
            "INSERT INTO alerts(timestamp, device_ip, description, severity) VALUES (?, ?, ?, ?)",
            (alert["timestamp"], alert["device_ip"], alert["description"], alert["severity"])
        )
        self.conn.commit()

    def count(self, table):
        return self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
