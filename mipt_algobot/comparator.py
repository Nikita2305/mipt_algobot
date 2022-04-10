from mipt_algobot.system_calls import *
import os
import time
import subprocess

ERROR_CODE = 143
FALSE_CODE = 144
TRUE_CODE = 0
DEFAULT_COMPARATOR = os.path.dirname(__file__) + "/tools/default_comp.cpp"

class comparator:
    def __init__(self):
        self.filename = DEFAULT_COMPARATOR
        self.exe_filename = ""
    def __del__(self):
        self.remove_executable()  
    def change_file(self, fname):
        if (fname != None):
            code, temp_exe_filename, verdict = compilation().compile(fname, COMPILATION_TIME_WAIT, False)
            if (code != COMPILATION_OK):
                return (False, "Comparator compilation failed. Verdict: \n" + verdict)
    
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
        if (self.exe_filename == ""):
            code, self.exe_filename, verdict = compilation().compile(self.filename, COMPILATION_TIME_WAIT, True)
            if (code != COMPILATION_OK):
                self.exe_filename = "" 
                return ERROR_CODE
        process = subprocess.run(self.exe_filename + " " + test + " " + output_ok + " " + output_user, shell=True)
        ex_code = process.returncode
        if (ex_code != TRUE_CODE and ex_code != FALSE_CODE):
            ex_code = ERROR_CODE
        return ex_code
