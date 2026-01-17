import re
from datetime import datetime

def utc():
    return datetime.utcnow().isoformat() + "Z"
