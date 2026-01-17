import yaml
from collections import defaultdict
from datetime import datetime, timedelta

class RuleEngine:
    def __init__(self, rules_file):
        with open(rules_file) as f:
            data = yaml.safe_load(f) or {}
        self.rules = data.get("rules", [])
        self.state = defaultdict(list)

    def process(self, log):
        alerts = []
        now = datetime.utcnow()

        for rule in self.rules:
            if rule["match"].lower() in log["message"].lower():
                if "threshold" in rule:
                    key = (rule["id"], log["source_ip"])
                    self.state[key].append(now)
                    window = timedelta(seconds=rule.get("window", 60))
                    self.state[key] = [t for t in self.state[key] if now - t <= window]

                    if len(self.state[key]) >= rule["threshold"]:
                        alerts.append(self._build_alert(rule, log))
                else:
                    alerts.append(self._build_alert(rule, log))

        return alerts

    def _build_alert(self, rule, log):
        return {
            "timestamp": log["timestamp"],
            "device_ip": log["source_ip"],
            "description": rule["description"],
            "severity": rule["severity"]
        }
