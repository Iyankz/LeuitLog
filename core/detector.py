class Detector:
    def __init__(self, rule_engine):
        self.rule_engine = rule_engine

    def analyze(self, log):
        return self.rule_engine.process(log)
