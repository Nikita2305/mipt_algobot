from mipt_algobot.task import *
import json

class contest:  
    def __init__(self, size = 0, l = ""):
        self.link = ""
        self.tasks = []
        for i in range(size):
            self.tasks += [task()]
        self.link = l 
    def dump(self, filename):
        d = dict()
        d["tasks"] = [task.dump() for task in self.tasks]
        d["link"] = self.link
        with open(filename, 'w') as f:
            print(json.dumps(d, ensure_ascii=False, indent=4), file=f)
    def load(self, filename): 
        with open(filename) as f:
            d = json.load(f)
        self.link = d["link"]
        for i in range(len(d["tasks"])):
            t = task()
            t.load(d["tasks"][i])
            self.tasks.append(t)
    def to_string(self):
        ret = "Contest: " + self.link + "\nTasks:\n"
        for i in range(len(self.tasks)):
            letter = chr(ord('A') + i)
            ret += letter + "\n"
            ret += self.tasks[i].to_string()
        return ret 
    def add_generator(self, gname, gfile, gprior, gtype, gdescription, taskletter):
        task_id = ord(taskletter) - ord('A')
        if (task_id < 0 or task_id >= len(self.tasks)):
            return (False, "Wrong task letter")
        return self.tasks[task_id].add_generator(gname, gfile, gprior, gtype, gdescription)
    def erase_generator(self, gname, taskletter):
        task_id = ord(taskletter) - ord('A')
        if (task_id < 0 or task_id >= len(self.tasks)):
            return (False, "Wrong task letter")
        return self.tasks[task_id].erase_generator(gname)
    def set_solution(self, fsolution, taskletter):
        task_id = ord(taskletter) - ord('A')
        if (task_id < 0 or task_id >= len(self.tasks)):
            return (False, "Wrong task letter")
        return self.tasks[task_id].set_solution(fsolution)
    def stress(self, fsolution, taskletter):
        task_id = ord(taskletter) - ord('A')
        if (task_id < 0 or task_id >= len(self.tasks)):
            return (False, "Wrong task letter")
        return self.tasks[task_id].stress(fsolution)
    def generators_to_string(self, taskletter):
        task_id = ord(taskletter) - ord('A')
        if (task_id < 0 or task_id >= len(self.tasks)):
            return (False, "Wrong task letter")
        return (True, self.tasks[task_id].generators_to_string())
