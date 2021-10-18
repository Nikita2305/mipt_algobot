import json

CHIEF_MANAGER, MANAGER, USER,  = range(3)

class access_manager:
    keys = dict()
    def __init__(self):
        pass
    def load(self, filename):
        with open(filename) as f:
            self.keys = json.load(f)
    def dump(self, filename):
        with open(filename, 'w') as f:
            print(json.dumps(self.keys, ensure_ascii=False, indent=4), file=f)
    def set_status(self, id, status):
        self.keys[id] = status
    def get_status(self, id):
        if not id in self.keys:
            self.set_status(id, USER)
        return self.keys[id];
    def get_managers(self):
        return [key for key in self.keys if self.keys[key] == MANAGER]
            
