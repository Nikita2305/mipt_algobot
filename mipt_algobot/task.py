from mipt_algobot.generator import *
from multiprocessing.pool import ThreadPool
import multiprocessing
import time
import os
from subprocess import Popen
import signal

TEST_COUNT = 500
CONST_TESTS = 10
ITERATIONS = 100
COMPILATION_TIME_WAIT = 4

def format_output(filename):
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
def fast_system_call(bash_command, time_limit):
    P = Popen(bash_command, shell=True, preexec_fn=os.setsid)
    TimeLimit = True
    for i in range(ITERATIONS):
        try:
            P.wait(time_limit / ITERATIONS)
            TimeLimit = False
            break
        except Exception:
            pass
    if (TimeLimit):
        try:
            os.killpg(os.getpgid(P.pid), signal.SIGTERM)
        except Exception:
            print("Killing process exception")
    return ((not TimeLimit), None)
"""

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
    return "sudo su vitek -c \"" + command + "\""

COMPILATION_OK, COMPILATION_TL, COMPILATION_ERROR, = range(3)

def comp(cpp_file):
    exe_file = "./mipt_algobot/temp/" + gen_timestamp()
    status, code = system_call("g++ -std=c++17 -O3 " + cpp_file + " -o " + exe_file, COMPILATION_TIME_WAIT)
    if not status:
        return (COMPILATION_TL, exe_file)
    if (code != 0):
        return (COMPILATION_ERROR, exe_file) 
    return (COMPILATION_OK, exe_file)

VERDICT_OK, VERDICT_WA, VERDICT_TL, VERDICT_ERROR, = range(4)

def compare(exe_OK, exe_TEST, test, TIME_WAIT):
    output1 = "./mipt_algobot/temp/" + gen_timestamp()
    OK1 = fast_system_call(exe_OK + " < " + test + " > " + output1, TIME_WAIT)[0]
    output2 = "./mipt_algobot/temp/user/" + gen_timestamp() 
    # OK2 = fast_system_call(exe_TEST + " < " + test + " > " + output2, TIME_WAIT)[0]
    OK2 = fast_system_call(vitek_bash(exe_TEST + " < " + test + " > " + output2), TIME_WAIT)[0] 
    if (not OK1):
        os.system("rm -f " + output1 + " " + output2)
        print("Author solution has TL!!!")
        return (VERDICT_ERROR, None)
    if (not OK2):
        os.system("sudo killall -u vitek")
        os.system("rm -f " + output1 + " " + output2)
        return (VERDICT_TL, None)
    try: 
        ret = compare_outputs(output1, output2)
    except Exception as e:
        print(e)
        os.system("rm -f " + output1 + " " + output2)
        return (VERDICT_ERROR, None) # TODO: fix this case. Ones output could be empty
    if (ret):
        os.system("rm -f " + output1 + " " + output2)
        return (VERDICT_OK, None)
    os.system("rm -f " + output2)
    return (VERDICT_WA, output1)

OKe = u'\U00002714'
FAILe = u'\U0000274c'

def passed_generators_to_string(lst):
    string = "Passed generators:\n"
    for gen in lst:
        string += gen[0] + ", " + str(gen[1]) + " tests\n"
    return string

class task:
    def __init__(self):
        self.time_limit = 1
        self.solution = None
        self.generators = []
    def load(self, jobj):
        self.solution = jobj["solution"]
        for gen in jobj["generators"]:
            g = generator(None, None, None, None, None)
            g.load(gen)
            self.generators.append(g)
        try:
            self.time_limit = jobj["time_limit"]
        except Exception: # TODO: убрать
            self.time_limit = 1
    def dump(self):
        jobj = dict()
        jobj["solution"] = self.solution
        jobj["generators"] = [gen.dump() for gen in self.generators];
        jobj["time_limit"] = self.time_limit
        return jobj
    def to_string(self):
        ret = "Time Limit: " + str(self.time_limit) + " seconds\n"
        ret += "Solution: " + (FAILe if self.solution == None else OKe) + "\n"
        ret += "Generators: " + (FAILe if len(self.generators) == 0 else OKe) + "\n"
        return ret
    def add_generator(self, gname, gfile, gpriority, gtype, gdescription):        
        for gen in self.generators:
            if gen.gen_name == gname:
                return (False, "There is such generator already!")
       
        test_gen = generator(gname, gfile, gpriority, gtype, gdescription) # to test
        filename = "./mipt_algobot/temp/to_check_generator.txt"
        if not test_gen.generate(filename):
            test_gen.clear(filename)
            return (False, "Generator execution failed")
        os.system("rm " + filename)

        inserted = False
        last_prior = 0
        i = 0
        BOUND_i = len(self.generators)
        while (True):
            if not (i < BOUND_i):
                break
            gen = self.generators[i]
            if (inserted):
                gen.priority += 1
            else:
                if (gpriority <= gen.priority):
                    self.generators.insert(i, generator(gname, gfile, gen.priority, gtype, gdescription))
                    BOUND_i += 1
                    inserted = True
                last_prior = gen.priority
            i += 1 
        if not inserted:
            self.generators.append(generator(gname, gfile, last_prior + 1, gtype, gdescription))

        return (True, "Generator has been added")
    def erase_generator(self, gname):
        FOUND = False
        BOUND_i = len(self.generators)
        i = 0
        while (True):
            if not (i < BOUND_i):
                break
            if (FOUND):
                self.generators[i].priority -= 1
            else:
                if (self.generators[i].gen_name == gname):
                    os.system("rm " + self.generators[i].filename)
                    self.generators.pop(i)
                    FOUND = True
                    BOUND_i -= 1
                    i -= 1 
            i += 1
            
        if (FOUND):
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
        if (temp_good[0] != COMPILATION_OK):
            os.system("rm " + temp_good[1])
            os.system("rm " + temp_check[1])
            return (False, "Author solution compilation failed")
        if (temp_check[0] != COMPILATION_OK):
            os.system("rm " + temp_good[1])
            os.system("rm " + temp_check[1])
            verdict = ("compilation error" if temp_check[0] == COMPILATION_ERROR else "time limit exceeded")
            return (False, "Your solution compilation failed. Verdict: " + verdict)
        temp_good = temp_good[1]
        temp_check = temp_check[1]

        multi_test_count = len([1 for gen in self.generators if gen.generator_type == MULTI_TEST]) 
        test_number = 0
        passed_generators = []
        for gen in self.generators:
            print("+ Generator")
            if (gen.generator_type == MULTI_TEST):
                tests_count = TEST_COUNT // multi_test_count
            else:
                tests_count = CONST_TESTS
            for i in range(tests_count):
                test_number += 1
                # print("Test " + str(test_number))
                if (gen.generate(filename)):
                    verdict, judge_answer = compare(temp_good, temp_check, filename, self.time_limit)
                    if (verdict == VERDICT_WA or verdict == VERDICT_TL):
                        os.system("rm " + temp_good)
                        os.system("rm " + temp_check)
                        gen.remove_executable()
                        return (True, "Test has been found! Verdict: " + ("WA(or RE or UB)" if verdict == VERDICT_WA else "TL (over " + str(self.time_limit) + " seconds)") + ", test failed: №" + str(test_number) + ".\n\n" + passed_generators_to_string(passed_generators) + "\nFailed generator:\n" + gen.description, filename, judge_answer)
                    gen.clear(filename)
                    if (verdict == VERDICT_ERROR):
                        os.system("rm " + temp_good)
                        os.system("rm " + temp_check)
                        gen.remove_executable()
                        return (False, "Author solution had TL or another error was occured")
                    
                else:
                    gen.remove_executable()
                    return (False, "Test generation failed")
            passed_generators += [(gen.description, tests_count)]
            gen.remove_executable()
        os.system("rm " + temp_good)
        os.system("rm " + temp_check)
        return (False, "Your solution seems OK. " + str(test_number) + " small tests were passed.\n\n" + passed_generators_to_string(passed_generators)) 
    def generators_to_string(self):
        return [str(gen.priority) + ". " + str(gen.gen_name) + " " + ("(multi)" if gen.generator_type == MULTI_TEST else "(single)") for gen in self.generators]
