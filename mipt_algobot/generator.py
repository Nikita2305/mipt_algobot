import os
import time

def gen_timestamp():
    s = str(time.time())
    return "".join(s.split('.'))

class generator:
    gen_name = ""
    filename = ""
    exe_filename = ""
    def __init__(self, gname, fname):
        self.gen_name = gname
        self.filename = fname
    def __del__(self):
        if (len(self.exe_filename) > 0):
            os.system("rm " + self.exe_filename)
    def dump(self):
        d = dict()
        d["name"] = self.gen_name
        d["path"] = self.filename
        return d
    def load(self, jobj):
        self.gen_name = d["name"]
        self.filename = d["path"]  
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
        
