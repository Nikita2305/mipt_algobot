import os
import time
import subprocess

ERROR_CODE = 143
FALSE_CODE = 144
TRUE_CODE = 0
DEFAULT_COMPARATOR = "./mipt_algobot/tools/default_comp.cpp"

def gen_timestamp():
    s = str(time.time())
    return "".join(s.split('.'))

class comparator:
    def __init__(self):
        self.filename = DEFAULT_COMPARATOR
        self.exe_filename = ""
    def __del__(self):
        self.remove_executable()  
    def change_file(self, fname):
        if (fname != None):
            ex_code = 0
            temp_exe_filename = "./mipt_algobot/temp/" + gen_timestamp()
            ex_code += os.system("g++ " + fname + " -o " + temp_exe_filename)
            if (ex_code > 0):
                return (False, "Comparator compilation failed")
            os.system("rm " + temp_exe_filename)
    
        self.remove_executable()
        self.remove_file()
        if (fname != None):
            self.filename = fname 
        return (True, "Comparator has been switched")
    def is_custom(self):
        if (self.filename == DEFAULT_COMPARATOR):
            return False
        return True
    def remove_executable(self):
        if (len(self.exe_filename) > 0):
            os.system("rm " + self.exe_filename)
            self.exe_filename = ""
    def remove_file(self):
        if (self.filename != DEFAULT_COMPARATOR):
            os.system("rm " + self.filename)
            self.filename = DEFAULT_COMPARATOR
    def dump(self):
        d = dict()
        d["path"] = self.filename
        return d
    def load(self, jobj):
        self.filename = jobj["path"]
    def compare_outputs(self, output_ok, output_user, test):
        ex_code = 0
        if (self.exe_filename == ""):
            self.exe_filename = "./mipt_algobot/temp/" + gen_timestamp()
            ex_code = os.system("g++ " + self.filename + " -o " + self.exe_filename)
        if (ex_code > 0):
            self.exe_filename = ""
            return ERROR_CODE
        process = subprocess.run(self.exe_filename + " " + test + " " + output_ok + " " + output_user, shell=True)
        ex_code = process.returncode
        if (ex_code != TRUE_CODE and ex_code != FALSE_CODE):
            ex_code = ERROR_CODE
        return ex_code

"""def format_output(filename):
    array = []
    temp = "./mipt_algobot/temp/" + gen_timestamp()
    with open(filename, 'r') as f:
        for line in f:
            array += line.split()
    with open(temp, 'w') as f:
        for word in array:
            f.write(word + "\n")
    return temp

def compare_outputs(output1, output2):
    out1 = format_output(output1)
    out2 = format_output(output2)
    with open(out1, 'r') as f:
        A1 = f.read()
    with open(out2, 'r') as f:
        A2 = f.read()
    ret = (A1 == A2)
    os.system("rm " + out1 + " " + out2)
    return ret
"""       
