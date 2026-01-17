import socket, yaml
from core.parser import parse_syslog
from core.storage import Storage
from core.rule_engine import RuleEngine
from core.detector import Detector

def run():
    with open('/etc/leuitlog/leuitlog.yaml') as f:
        config = yaml.safe_load(f)

    storage = Storage(config['storage']['db'])
    engine = RuleEngine('/etc/leuitlog/rules.yaml')
    detector = Detector(engine)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', config['syslog']['udp_port']))

    while True:
        data, addr = sock.recvfrom(8192)
        log = parse_syslog(data, addr[0])
        log['severity'] = 'INFO'
        storage.insert_log(log)

        for alert in detector.analyze(log):
            storage.insert_alert(alert)

if __name__ == '__main__':
    run()
