from mipt_algobot.generator import *
import filecmp
from multiprocessing.pool import ThreadPool
import multiprocessing
import time
import os

TEST_COUNT = 500
TIME_WAIT = 1
ITERATIONS = 100
COMPILATION_TIME_WAIT = 4

def fast_system_call(bash_command, time_limit):
    T = multiprocessing.Process(target=os.system, args=(bash_command,))
    T.start()
    TimeLimit = True
    for i in range(ITERATIONS):
        time.sleep(time_limit / ITERATIONS)
        if not T.is_alive():
            TimeLimit = False
            break
    T.terminate()
    return ((not TimeLimit), None)

def system_call(bash_command, time_limit):
    pool = ThreadPool(processes=1)
    async_result = pool.apply_async(os.system, (bash_command, ))
    TimeLimit = True
    for i in range(ITERATIONS):
        time.sleep(time_limit / ITERATIONS)
        if async_result.ready():
            TimeLimit = False
            break
    if (TimeLimit): 
        ret = (False, None)
    else:
        ret = (True, async_result.get())
    pool.terminate()
    return ret

def vitek_path(path):
    return os.path.relpath(path, "./mipt_algobot/temp/user")
    
def vitek_bash(command):
    return "sudo runuser -l vitek -c \"" + command + "\""

def comp(cpp_file):
    exe_file = "./mipt_algobot/temp/" + gen_timestamp()
    status, code = system_call("g++ " + cpp_file + " -o " + exe_file, COMPILATION_TIME_WAIT) 
    return (status and (code == 0), exe_file)

VERDICT_OK, VERDICT_WA, VERDICT_TL, VERDICT_ERROR, = range(4)

def compare(exe_OK, exe_TEST, test): 
    output1 = "./mipt_algobot/temp/" + gen_timestamp()
    OK1 = fast_system_call(exe_OK + " < " + test + " > " + output1, TIME_WAIT)[0]
    output2 = "./mipt_algobot/temp/user/" + gen_timestamp() 
    OK2 = fast_system_call(vitek_bash(vitek_path(exe_TEST) + " < " + vitek_path(test) + " > " + vitek_path(output2)), TIME_WAIT)[0]
    if (not OK1):
        os.system("rm " + output1)
        os.system(vitek_bash("rm " + vitek_path(output2)))
        return VERDICT_ERROR
    if (not OK2):
        os.system("rm " + output1)
        os.system(vitek_bash("rm " + vitek_path(output2)))
        return VERDICT_TL
    try: 
        ret = filecmp.cmp(output1, output2)
    except Exception:
        os.system("rm " + output1)
        os.system(vitek_bash("rm " + vitek_path(output2)))
        return VERDICT_WA
    os.system("rm " + output1)
    os.system(vitek_bash("rm " + vitek_path(output2)))
    return (VERDICT_OK if ret else VERDICT_WA)

OKe = u'\U00002714'
FAILe = u'\U0000274c'

class task:
    def __init__(self):
        self.solution = None
        self.generators = []
    def load(self, jobj):
        self.solution = jobj["solution"]
        self.generators = [generator(gen["name"], gen["path"]) for gen in jobj["generators"]]
    def dump(self):
        jobj = dict()
        jobj["solution"] = self.solution
        jobj["generators"] = [gen.dump() for gen in self.generators];
        return jobj
    def to_string(self):
        ret = "Solution: " + (FAILe if self.solution == None else OKe) + "\n"
        ret += "Generators: " + (FAILe if len(self.generators) == 0 else OKe) + "\n"
        return ret
    def add_generator(self, gname, gfile):
        for gen in self.generators:
            if gen.gen_name == gname:
                return (False, "There is such generator already!")
        self.generators.append(generator(gname, gfile))
        filename = "./mipt_algobot/temp/to_check_generator.txt"
        if (self.generators[-1].generate(filename)):
            self.generators[-1].clear(filename)
            return (True, "Generator has been added")
        else:
            self.generators.pop()
            return (False, "Generator execution failed")
    def erase_generator(self, gname):
        for i in range(len(self.generators)):
            index = len(self.generators) - i - 1
            if (self.generators[index].gen_name == gname):
                os.system("rm " + self.generators[index].filename)
                self.generators.pop(index)
                return (True, "Generator has been erased")
        return (False, "Generator not found")
    def set_solution(self, fsolution):
        if (self.solution != None):
            os.system("rm " + self.solution)
        self.solution = fsolution
        return (True, "Solution has been switched")
    def stress(self, fsolution):
        if (self.solution == None or len(self.generators) == 0):
            return (False, "Task is not complete")
        filename = "./mipt_algobot/temp/input.txt"
        temp_good = comp(self.solution)
        temp_check = comp(fsolution)
        if (not temp_good[0]):
            os.system("rm " + temp_good[1])
            os.system("rm " + temp_check[1])
            return (False, "Author solution compilation failed")
        if (not temp_check[0]):
            os.system("rm " + temp_good[1])
            os.system("rm " + temp_check[1])
            return (False, "Your solution compilation failed")
        temp_good = temp_good[1]
        temp_check = temp_check[1]
        for i in range(TEST_COUNT):
            print("Test " + str(i))
            gen = self.generators[i % len(self.generators)]
            if (gen.generate(filename)):
                verdict = compare(temp_good, temp_check, filename)
                if (verdict == VERDICT_WA or verdict == VERDICT_TL):
                    os.system("rm " + temp_good)
                    os.system("rm " + temp_check)
                    return (True, "Test has been found! Verdict: " + ("WA" if verdict == VERDICT_WA else "TL"), filename)
                if (verdict == VERDICT_ERROR):
                    os.system("rm " + temp_good)
                    os.system("rm " + temp_check)
                    return (False, "Author solution had TL")
                gen.clear(filename)
        os.system("rm " + temp_good)
        os.system("rm " + temp_check)
        return (False, "Your solution seems OK.")
    def generators_names(self):
        return [gen.gen_name for gen in self.generators]
