import os
import time

SINGLE_TEST, MULTI_TEST, = range(2)

def gen_timestamp():
    s = str(time.time())
    return "".join(s.split('.'))

class generator:
    gen_name = ""
    filename = ""
    exe_filename = ""
    priority = None
    generator_type = None
    description = ""
    def __init__(self, gname, fname, priority, generator_type, description):
        self.gen_name = gname
        self.filename = fname
        self.priority = priority
        self.generator_type = generator_type
        self.description = description
    def __del__(self):
        self.remove_executable()    
    def remove_executable(self):
        if (len(self.exe_filename) > 0):
            os.system("rm " + self.exe_filename)
            self.exe_filename = ""
    def dump(self):
        d = dict()
        d["name"] = self.gen_name
        d["path"] = self.filename
        d["prior"] = self.priority
        d["type"] = self.generator_type
        d["description"] = self.description
        return d
    def load(self, jobj):
        self.gen_name = jobj["name"]
        self.filename = jobj["path"]
        self.priority = jobj["prior"]
        self.generator_type = jobj["type"]
        self.description = jobj["description"]
    def generate(self, output_filename):
        ex_code = 0
        if (self.exe_filename == ""):
            self.exe_filename = "./mipt_algobot/temp/" + gen_timestamp()
            ex_code += os.system("g++ " + self.filename + " -o " + self.exe_filename)
        if (ex_code > 0): 
            return False
        ex_code += os.system(self.exe_filename + " > " + output_filename)
        return ex_code == 0
    def clear(self, output_filename):
        os.system("rm " + output_filename)
        
