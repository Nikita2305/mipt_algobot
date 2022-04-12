from mipt_algobot.generator import *
from mipt_algobot.comparator import *
from mipt_algobot.system_calls import *
import os

TEST_COUNT = 500
CONST_TESTS = 10

vitek_root = os.path.dirname(__file__) + "/temp/user"

def vitek_path(path): 
    return os.path.relpath(path, vitek_root)
    
def vitek_bash(command):
    return "cd " + vitek_root + ";sudo su vitek -c \"" + command + "\""

VERDICT_OK, VERDICT_WA, VERDICT_TL, VERDICT_ERROR, = range(4)

def compare(exe_OK, exe_TEST, test, self_comparator, TIME_WAIT):
    output1 = os.path.dirname(__file__) + "/temp/" + gen_timestamp()
    OK1 = fast_system_call(exe_OK + " < " + test + " > " + output1, TIME_WAIT)[0]
    output2 = os.path.dirname(__file__) + "/temp/user/" + gen_timestamp() 
    # OK2 = fast_system_call(exe_TEST + " < " + test + " > " + output2, TIME_WAIT)[0]
    OK2 = fast_system_call(vitek_bash(vitek_path(exe_TEST) + " < " + vitek_path(test) + " > " + vitek_path(output2)), TIME_WAIT)[0]
    if (not OK1):
        os.system("rm -f " + output1 + " " + output2)
        return (VERDICT_ERROR, None)
    if (not OK2):
        os.system("sudo killall -u vitek")
        os.system("rm -f " + output1 + " " + output2)
        return (VERDICT_TL, None)
    try: 
        ret = self_comparator.compare_outputs(output1, output2, test)
        if (ret == ERROR_CODE):
            raise Exception("Error while executing")
        ret = (True if ret == TRUE_CODE else False)
    except Exception as e:
        os.system("rm -f " + output1 + " " + output2)
        return (VERDICT_ERROR, None)
    if (ret):
        os.system("rm -f " + output1 + " " + output2)
        return (VERDICT_OK, None)
    os.system("rm -f " + output2)
    return (VERDICT_WA, output1)

OKe = u'\U00002714'
FAILe = u'\U0000274c'
SMILE = u'\U0001F60A'
COOL_SMILE = u'\U0001F60E'

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
        self.comparator = comparator()
    def load(self, jobj):
        self.solution = jobj["solution"]
        for gen in jobj["generators"]:
            g = generator(None, None, None, None, None)
            g.load(gen)
            self.generators.append(g)
        self.time_limit = jobj["time_limit"]
        self.comparator = comparator()
        self.comparator.load(jobj["comparator"])
    def dump(self):
        jobj = dict()
        jobj["solution"] = self.solution
        jobj["generators"] = [gen.dump() for gen in self.generators];
        jobj["time_limit"] = self.time_limit
        jobj["comparator"] = self.comparator.dump()
        return jobj
    def to_string(self):
        ret = "Time Limit: " + str(self.time_limit) + " seconds\n"
        ret += "Solution: " + (FAILe if self.solution == None else OKe) + "\n"
        ret += "Generators: " + (FAILe if len(self.generators) == 0 else OKe) + "\n"
        ret += "Comparator: " + (COOL_SMILE if self.comparator.is_custom() else SMILE) + "\n"
        return ret
    def add_generator(self, gname, gfile, gpriority, gtype, gdescription):        
        for gen in self.generators:
            if gen.gen_name == gname:
                return (False, "There is such generator already!")
       
        test_gen = generator(gname, gfile, gpriority, gtype, gdescription) # to test
        filename = os.path.dirname(__file__) + "/temp/to_check_generator.txt"
        flag, verdict = test_gen.generate(filename)
        if not flag:
            test_gen.clear(filename)
            return (False, "Generator execution failed. Verdict: \n" + verdict)
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
        return (False, "Generator was not found")
    def set_solution(self, fsolution):
        code, executable, verdict = compilation().compile(fsolution, COMPILATION_TIME_WAIT, False)
        if (code != COMPILATION_OK):
            return (False, "Compilation failed. Verdict: \n" + verdict)
        if (self.solution != None):
            os.system("rm " + self.solution)
        self.solution = fsolution
        return (True, "Solution has been switched")
    def set_comparator(self, fcomparator):
        return self.comparator.change_file(fcomparator) 
    def stress(self, fsolution): 
        if (self.solution == None or len(self.generators) == 0):
            return (False, "Task is not complete")
        filename = os.path.dirname(__file__) + "/temp/input.txt"
        temp_good = compilation().compile(self.solution, COMPILATION_TIME_WAIT, True)
        temp_check = compilation().compile(fsolution, COMPILATION_TIME_WAIT, True)
        if (temp_good[0] != COMPILATION_OK):
            os.system("rm " + temp_good[1])
            os.system("rm " + temp_check[1])
            return (False, "Author solution compilation failed")
        if (temp_check[0] != COMPILATION_OK):
            os.system("rm " + temp_good[1])
            os.system("rm " + temp_check[1])
            return (False, "Your solution compilation failed. Verdict: \n" + temp_check[2])
        temp_good = temp_good[1]
        temp_check = temp_check[1]

        multi_test_count = len([1 for gen in self.generators if gen.generator_type == MULTI_TEST]) 
        test_number = 0
        passed_generators = []
        for gen in self.generators:
            if (gen.generator_type == MULTI_TEST):
                tests_count = TEST_COUNT // multi_test_count
            else:
                tests_count = CONST_TESTS
            for i in range(tests_count):
                test_number += 1
                if (gen.generate(filename)[0]):
                    verdict, judge_answer = compare(temp_good, temp_check, filename, self.comparator, self.time_limit)
                    if (verdict == VERDICT_WA or verdict == VERDICT_TL):
                        os.system("rm " + temp_good)
                        os.system("rm " + temp_check)
                        self.comparator.remove_executable()
                        gen.remove_executable()
                        return (True, "Test has been found! Verdict: " + ("WA(or RE or UB)" if verdict == VERDICT_WA else "TL (over " + str(self.time_limit) + " seconds)") + ", test failed: №" + str(test_number) + ".\n\n" + passed_generators_to_string(passed_generators) + "\nFailed generator:\n" + gen.description, filename, judge_answer)
                    gen.clear(filename)
                    if (verdict == VERDICT_ERROR):
                        os.system("rm " + temp_good)
                        os.system("rm " + temp_check)
                        self.comparator.remove_executable()
                        gen.remove_executable()
                        return (False, "Author solution had TL or another error was occured")
                    
                else:
                    self.comparator.remove_executable()
                    gen.remove_executable()
                    return (False, "Test generation failed")
            passed_generators += [(gen.description, tests_count)]
            gen.remove_executable()
        os.system("rm " + temp_good)
        os.system("rm " + temp_check)
        self.comparator.remove_executable()
        return (False, "Your solution seems OK. " + str(test_number) + " tests were passed.\n\n" + passed_generators_to_string(passed_generators)) 
    def generators_to_string(self):
        return [str(gen.priority) + ". " + str(gen.gen_name) + " " + ("(multi)" if gen.generator_type == MULTI_TEST else "(single)") for gen in self.generators]
