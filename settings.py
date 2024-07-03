import json


class Settings:
    enabled = 0
    volume = 0
    input = 0
    sw = 0
    treble = 0
    bass = 0
    balance = 0

    def __init__(self):
        self.enabled =0
        self.volume = 0
        self.input = 0
        self.sw = 0
        self.treble = 0
        self.bass = 0
        self.balance = 0

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["enabled"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.enabled = 0
    def to_json(self):
        return json.dumps(self.__dict__)
