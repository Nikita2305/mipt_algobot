from mipt_algobot.contest import *
from mipt_algobot.access_manager import *
from functools import wraps

contest_path = "contest/contest.txt"
contest = contest()
try:
    contest.load(contest_path)
except Exception:
    pass

manager_path = "temp/access_manager.txt"
access_manager = access_manager()
try:
    access_manager.load(manager_file)
except Exception:
    pass

def f(id):
    print("F")

def g(id):
    print("G")

permissions = { USER : [f],
                MANAGER : [f, g],
                CHIEF_MANAGER: [f, g] }

def access_decorator(function):
    @wraps(function)
    def decorated(id):
        if (not function in permissions[access_manager.get_status(id)]):
            print("^(")
            return
        function(id)
    return decorated

f = access_decorator(f)
g = access_decorator(g)


admin_id = 123
man_id = 234
u_id = -1
access_manager.set_status(admin_id, CHIEF_MANAGER)
access_manager.set_status(man_id, MANAGER)

f(admin_id)
f(man_id)
f(u_id)
g(admin_id)
g(man_id)
g(u_id)

access_manager.dump(manager_path)
contest.dump(contest_path)
