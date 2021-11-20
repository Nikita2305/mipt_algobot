from multiprocessing.pool import ThreadPool
import multiprocessing
import time
import os

COMPILATION_OK, COMPILATION_TL, COMPILATION_ERROR, = range(3)
COMPILATION_TIME_WAIT = 5
ITERATIONS = 100

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

def gen_timestamp():
    s = str(time.time())
    return "".join(s.split('.'))

class compilation:
    def __init__(self):
        self.status = "" 

    def compile(self, cpp_file, time_limit, return_exe):
        exe_file = "./mipt_algobot/temp/" + gen_timestamp()
        log_file = "./mipt_algobot/temp/" + gen_timestamp() + ".txt"
        status, code = system_call("g++ -std=c++17 -O3 " + cpp_file + " -o " + exe_file + " >" + log_file + " 2>&1", time_limit)
        try:
            with open(log_file, "r") as f:
                self.status = f.read()
        except Exception:
            self.status = ""
        os.system("rm " + log_file)
        if not status:
            self.status = "time limit exceeded (" + str(time_limit) + " s)" 
            return (COMPILATION_TL, exe_file, self.status)
        if (code != 0):
            return (COMPILATION_ERROR, exe_file, self.status)
        if not return_exe:
            os.system("rm " + exe_file)
        return (COMPILATION_OK, exe_file, self.status)

