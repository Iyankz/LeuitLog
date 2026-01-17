#!/usr/bin/env python3
from core.storage import Storage

db = Storage("/var/lib/leuitlog/leuitlog.db")

print("Logs:", db.count("logs"))
print("Devices:", db.count("devices"))
print("Alerts:", db.count("alerts"))
