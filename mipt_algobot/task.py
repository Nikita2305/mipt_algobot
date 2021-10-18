from mipt_algobot.generator import *
import filecmp
import multiprocessing
import time

def comp(cpp_file):
    exe_file = "./mipt_algobot/temp/" + gen_timestamp()
    code = os.system("g++ " + cpp_file + " -o " + exe_file)
    return (bool(code == 0), exe_file)

'''
code1 = None
code2 = None
'''

'''global code1
    global code2
    code1 = None
    code2 = None'''

'''print(code1, code2)
    if (code1 == None or code2 == None or code1 + code2 != 0): 
        os.system("rm " + output1 + " " + output2)
        return False
    '''

def execute1(string):
    os.system(string)

def execute2(string):
    os.system(string)

def compare(exe1, exe2, test): 
    output1 = "./mipt_algobot/temp/" + gen_timestamp()
    T1 = multiprocessing.Process(target=execute1, args=(exe1 + " < " + test + " > " + output1,))
    T1.start()
    output2 = "./mipt_algobot/temp/" + gen_timestamp()
    T2 = multiprocessing.Process(target=execute2, args=(exe2 + " < " + test + " > " + output2,))
    T2.start()
    time.sleep(0.5)
    T1.terminate()
    T2.terminate()
    try: 
        ret = filecmp.cmp(output1, output2)
    except Exception:
        os.system("rm " + output1 + " " + output2)
        return False
    os.system("rm " + output1 + " " + output2)
    return ret

OKe = u'\U00002714'
FAILe = u'\U0000274c'

class task:
    solution = None
    generators = []
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
            return (True, "Generator have been added")
        else:
            self.generators.pop()
            return (False, "Generator execution failed")
    def erase_generator(self, gname):
        for i in range(len(self.generators)):
            index = len(self.generators) - i - 1
            if (self.generators[index].gen_name == gname):
                os.system("rm " + self.generators[index].filename)
                self.generators.pop(index)
                return (True, "Generator have been erased")
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
            return (False, "Author solution execution failed")
        if (not temp_good[0]):
            os.system("rm " + temp_good[1])
            os.system("rm " + temp_check[1])
            return (False, "Your solution execution failed")
        temp_good = temp_good[1]
        temp_check = temp_check[1]
        for i in range(1000):
            gen = self.generators[i % len(self.generators)]
            if (gen.generate(filename)):
                if (not compare(temp_good, temp_check, filename)):
                    gen.clear(temp_good)
                    gen.clear(temp_check)
                    return (True, "Test have been found!", filename)
                gen.clear(filename)
        os.system("rm " + temp_good)
        os.system("rm " + temp_check)
        return (False, "Your solution seems OK")
    def generators_names(self):
        return [gen.gen_name for gen in self.generators]
