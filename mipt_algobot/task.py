from mipt_algobot.generator import *
import filecmp
from multiprocessing.pool import ThreadPool
import multiprocessing
import time
import os

TEST_COUNT = 500
CONST_TESTS = 10
TIME_WAIT = 1
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
    ret = filecmp.cmp(out1, out2)
    os.system("rm " + out1 + " " + out2)
    return ret

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
    status, code = system_call("g++ -O3 " + cpp_file + " -o " + exe_file, COMPILATION_TIME_WAIT)
    if not status:
        return (COMPILATION_TL, exe_file)
    if (code != 0):
        return (COMPILATION_ERROR, exe_file) 
    return (COMPILATION_OK, exe_file)

VERDICT_OK, VERDICT_WA, VERDICT_TL, VERDICT_ERROR, = range(4)

def compare(exe_OK, exe_TEST, test):
    output1 = "./mipt_algobot/temp/" + gen_timestamp()
    OK1 = fast_system_call(exe_OK + " < " + test + " > " + output1, TIME_WAIT)[0]
    output2 = "./mipt_algobot/temp/user/" + gen_timestamp() 
    OK2 = fast_system_call(vitek_bash(exe_TEST + " < " + test + " > " + output2), TIME_WAIT)[0]
    if (not OK1):
        os.system("rm -f " + output1 + " " + output2)
        print("Author solution has TL!!!")
        return (VERDICT_ERROR, None)
    if (not OK2):
        os.system("rm -f " + output1 + " " + output2)
        return (VERDICT_TL, None)
    try: 
        ret = compare_outputs(output1, output2)
    except Exception as e:
        print(e)
        os.system("rm -f " + output1 + " " + output2)
        return (VERDICT_ERROR, None)
    if (ret):
        os.system("rm -f " + output1 + " " + output2)
        return (VERDICT_OK, None)
    os.system("rm -f " + output2)
    return (VERDICT_WA, output1)

OKe = u'\U00002714'
FAILe = u'\U0000274c'

class task:
    def __init__(self):
        self.solution = None
        self.generators = []
    def load(self, jobj):
        self.solution = jobj["solution"]
        for gen in jobj["generators"]:
            g = generator(None, None, None, None)
            g.load(gen)
            self.generators.append(g)
    def dump(self):
        jobj = dict()
        jobj["solution"] = self.solution
        jobj["generators"] = [gen.dump() for gen in self.generators];
        return jobj
    def to_string(self):
        ret = "Solution: " + (FAILe if self.solution == None else OKe) + "\n"
        ret += "Generators: " + (FAILe if len(self.generators) == 0 else OKe) + "\n"
        return ret
    def add_generator(self, gname, gfile, gpriority, gtype):        
        for gen in self.generators:
            if gen.gen_name == gname:
                return (False, "There is such generator already!")
       
        test_gen = generator(gname, gfile, gpriority, gtype) # to test
        filename = "./mipt_algobot/temp/to_check_generator.txt"
        if not test_gen.generate(filename):
            test_gen.clear(filename)
            return (False, "Generator execution failed")
        os.system("rm " + filename)

        inserted = False
        last_prior = 0
        for i in range(len(self.generators)):
            gen = self.generators[i]
            if (inserted):
                gen.priority += 1
            else:
                if (gpriority <= gen.priority):
                    self.generators.insert(i, generator(gname, gfile, gen.priority, gtype))
                    inserted = True
                last_prior = gen.priority 
        if not inserted:
            self.generators.append(generator(gname, gfile, last_prior + 1, gtype))

        return (True, "Generator has been added")
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
        for gen in self.generators:
            print("+ Generator")
            if (gen.generator_type == MULTI_TEST):
                tests_count = TEST_COUNT // multi_test_count
            else:
                tests_count = CONST_TESTS
            for i in range(tests_count):
                test_number += 1
                print("Test " + str(test_number))
                if (gen.generate(filename)):
                    verdict, judge_answer = compare(temp_good, temp_check, filename)
                    if (verdict == VERDICT_WA or verdict == VERDICT_TL):
                        os.system("rm " + temp_good)
                        os.system("rm " + temp_check)
                        return (True, "Test has been found! Verdict: " + ("WA(or RE or UB)" if verdict == VERDICT_WA else "TL") + ", test failed: №" + str(test_number), filename, judge_answer)
                    if (verdict == VERDICT_ERROR):
                        os.system("rm " + temp_good)
                        os.system("rm " + temp_check)
                        return (False, "Author solution had TL or another error was occured")
                    gen.clear(filename)
                else:
                    return (False, "Test generation failed")
        os.system("rm " + temp_good)
        os.system("rm " + temp_check)
        return (False, "Your solution seems OK. " + str(test_number) + " small tests were passed.")
    def generators_names(self):
        return [gen.gen_name for gen in self.generators]
