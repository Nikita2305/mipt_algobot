import logging
import os
from mipt_algobot.contest import *
from mipt_algobot.access_manager import *
from functools import wraps

ADMIN_ID = "305197734"
# BOT_KEY = "2059860302:AAH7O8SvtX2PT-NVrpLt7Ejk_aE6WqQRNBo" # TODO test bot
BOT_KEY = "1716312395:AAHNG2oy48lC-EnuLfCYCO80IVHUGrNODS8"

from telegram import (
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ParseMode, 
    Document
)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters, 
    ConversationHandler
)

def dump_system():
    global access_manager_obj
    global contest_obj
    access_manager_obj.dump(manager_path)
    contest_obj.dump(contest_path)    

def cancel_decorator(function):
    @wraps(function)
    def decorated(update, context):
        if (update.message.text == "/cancel"):
            return cancel(update, context)
        ret = function(update, context)
        dump_system()
        return ret
    return decorated

def access_decorator(function):
    @wraps(function)
    def decorated(update, context):
        if (not function in permissions[access_manager_obj.get_status(str(update.effective_user.id))]):
            update.message.reply_text("Нет доступа, обращайтесь к админу")
            return ConversationHandler.END
        ret = function(update, context)
        dump_system()
        return ret
    return decorated

def feedback_decorator(function):
    @wraps(function)
    def decorated(update, context):
        context.bot.send_message(int(ADMIN_ID),
    """
Feedback
Text: """ + str(update.message.text) + """
Id: """ + str(update.effective_user.id) + """
Username: @""" + str(update.effective_user.username)
        )
        return function(update, context)
    return decorated

# TODO: /report - to make service better.
# It's done(search for "report" in code),
# but with no response from mine to user. Fix that. 

def help_text(update, context):
    update.message.reply_text(
    """
/help - to see this message
/guide - to know basics of interaction

*For users*
/contest
/get\_id
/stress - core function
/cancel

*For managers*
/rules
/set\_solution
/add\_generator
/erase\_generator
/set\_tl
/set\_comparator

*For chief manager*
/set\_contest
/add\_manager
/erase\_manager
/managers
/kill
    """, parse_mode=ParseMode.MARKDOWN)

def guide(update, context):
    update.message.reply_text(
    """
1. Нажми /contest, чтобы узнать, какой сейчас контест и какие в нём есть задачи.
2. Проверь, что по нужной тебе задаче стоят две галочки.
3. Нажми /stress, чтобы протестировать своё решение.
    """, parse_mode=ParseMode.MARKDOWN)

def get_id(update, context):
    update.message.reply_text(str(update.effective_user.id))

def rules(update, context):
    update.message.reply_text(
    """
*Важные вещи*
1. Создание нового контеста уничтожает старый
2. Добавление нового решения удаляет старое
3. Засылай только ACCEPTED решения
4. Засылай только работающие генераторы
5. Не удаляй чужие генераторы  
    """, parse_mode=ParseMode.MARKDOWN)

TYPING_ID_STATE = 0

def add_manager_entry(update, context):
    update.message.reply_text("Введите его id, или /cancel, если не знаете")
    return TYPING_ID_STATE

def add_manager(update, context):
    access_manager_obj.set_status(update.message.text, MANAGER)
    update.message.reply_text("Добавлен " + update.message.text)
    return ConversationHandler.END

def erase_manager_entry(update, context):
    update.message.reply_text("Введите его id, или /cancel, если не знаете")
    return TYPING_ID_STATE

def erase_manager(update, context): 
    access_manager_obj.set_status(update.message.text, USER)
    update.message.reply_text("Удалён " + update.message.text)
    return ConversationHandler.END

def get_managers(update, context):
    ret = access_manager_obj.get_managers()
    s = "Вот они, сверху вниз:\n"
    for x in ret:
        s += x
        s += "\n"
    update.message.reply_text(s)  

TYPING_CONTESTSIZE_STATE, TYPING_CONTESTLINK_STATE, = range(2)

def set_contest_entry(update, context):
    update.message.reply_text("Введите одно число - количество задач(или /cancel)")
    return TYPING_CONTESTSIZE_STATE

def set_contest_size(update, context):
    size = update.message.text
    try:
        size = int(size)
    except Exception:
        return cancel(update, context)
    context.user_data['size'] = size
    update.message.reply_text("Введите строку - ссылку на контест(или /cancel)")
    return TYPING_CONTESTLINK_STATE

def set_contest_link(update, context):
    global contest_obj
    temp_filename = "mipt_algobot/temp/temp.tar.gz"
    os.system("tar -czvf " + temp_filename + " mipt_algobot/contest")
    update.message.reply_document(
        open(temp_filename, 'rb'), 
        filename="prev_cont.tar.gz",
        caption="Your previous contest"
    )
    os.system("sh " + os.path.dirname(__file__) + "/../scripts/restart.sh")
    contest_obj = contest(context.user_data['size'], update.message.text)
    update.message.reply_text("Создан контест на " + str(context.user_data['size']) +" задач")
    return ConversationHandler.END

TYPING_TIMELIMIT_LETTER_STATE, TYPING_TIMELIMIT_VALUE_STATE, = range(2)

def set_timelimit_entry(update, context):
    update.message.reply_text("Введите заглавную букву задачи(или /cancel)")
    return TYPING_TIMELIMIT_LETTER_STATE

def set_timelimit_letter(update, context):
    if not len(update.message.text) == 1:
        return cancel(update, context)
    context.user_data['letter'] = update.message.text;
    update.message.reply_text("Ожидаю целое число - время в секундах (или /cancel)")
    return TYPING_TIMELIMIT_VALUE_STATE 

def set_timelimit_value(update, context):
    global contest_obj
    value = update.message.text
    try:
        value = int(value)
    except Exception:
        return cancel(update, context)
    res = contest_obj.set_time_limit(value, context.user_data['letter'])
    update.message.reply_text(res[1])
    return ConversationHandler.END

def contest_info(update, context):
    global contest_obj
    update.message.reply_text(contest_obj.to_string())

SOLUTION_LETTER_STATE, SOLUTION_FILE_STATE = range(2)

def set_solution_entry(update, context):
    update.message.reply_text("Введите заглавную букву задачи(или /cancel)")
    return SOLUTION_LETTER_STATE

def set_solution_letter(update, context):
    if not len(update.message.text) == 1:
        return cancel(update, context)
    context.user_data['letter'] = update.message.text;
    update.message.reply_text("Ожидаю файл - решение по задаче " +  update.message.text + ". (или /cancel)")
    return SOLUTION_FILE_STATE

def set_solution_file(update, context):
    global contest_obj
    solution_path = os.path.dirname(__file__) + "/contest/solutions/" + context.user_data['letter'] + gen_timestamp() + ".cpp"
    f = context.bot.getFile(update.message.document.file_id)
    f.download(solution_path)
    res = contest_obj.set_solution(solution_path, context.user_data['letter'])
    update.message.reply_text(res[1])
    if (not res[0]):
        os.system("rm " + solution_path)
    return ConversationHandler.END 

COMPARATOR_LETTER_STATE, COMPARATOR_FILE_STATE, = range(2)

def set_comparator_entry(update, context):
    update.message.reply_text("Введите заглавную букву задачи(или /cancel)")
    return COMPARATOR_LETTER_STATE

def set_comparator_letter(update, context):
    if not len(update.message.text) == 1:
        return cancel(update, context)
    context.user_data['letter'] = update.message.text;
    update.message.reply_text("Ожидаю /default или файл - компаратор по задаче " +  update.message.text + ". (или /cancel)")
    return COMPARATOR_FILE_STATE

def set_comparator_file(update, context):
    global contest_obj
    comparator_path = os.path.dirname(__file__) + "/contest/comparators/" + context.user_data['letter'] + gen_timestamp() + ".cpp"
    f = context.bot.getFile(update.message.document.file_id)
    f.download(comparator_path)
    res = contest_obj.set_comparator(comparator_path, context.user_data['letter'])
    update.message.reply_text(res[1])
    if not res[0]:
        os.system("rm " + comparator_path)
    return ConversationHandler.END 

def set_comparator_default(update, context):
    global contest_obj
    res = contest_obj.set_comparator(None, context.user_data['letter'])
    update.message.reply_text(res[1])
    return ConversationHandler.END 

ADD_GENERATOR_LETTER_STATE, ADD_GENERATOR_NAME_STATE, ADD_GENERATOR_DESCRIPTION_STATE, ADD_GENERATOR_PRIORITY_STATE, ADD_GENERATOR_TYPE_STATE, ADD_GENERATOR_FILE_STATE, = range(6)

def add_generator_entry(update, context):
    update.message.reply_text("Введите заглавную букву задачи(или /cancel)")
    return ADD_GENERATOR_LETTER_STATE

def add_generator_letter(update, context):
    global contest_obj
    if not len(update.message.text) == 1:
        return cancel(update, context)
    context.user_data['letter'] = update.message.text;
    res = contest_obj.generators_to_string(update.message.text)
    if not res[0]:
        update.message.reply_text(res[1])
        return cancel(update, context)
    update.message.reply_text("Генераторы этой задаче:\n" + "\n".join(res[1]))
    update.message.reply_text("Введите название вашего генератора (или /cancel)")
    return ADD_GENERATOR_NAME_STATE

def correct_file_name(filename):
    filename = filename.lower()
    for c in filename:
        if not (c.isalpha() or c.isdigit() or c == '_'):
            return False
    return True 

def add_generator_name(update, context): 
    if (not correct_file_name(update.message.text)):
        update.message.reply_text("Некорректное имя генератора, пожалуйста, используйте латинские буквы, цифры и нижние подчёркивания")
        return cancel(update, context)
    context.user_data['gen_name'] = update.message.text;
    update.message.reply_text("Введите описание к генератору, можно на русском даже. Оно будет показано студентам. (или /cancel)")
    return ADD_GENERATOR_DESCRIPTION_STATE
 
def add_generator_description(update, context):
    context.user_data['gen_description'] = update.message.text;
    update.message.reply_text("Введите приоритет (число от 1 до +inf - место, на которое встанет ваш генератор) или /cancel.") 
    return ADD_GENERATOR_PRIORITY_STATE

def add_generator_priority(update, context):
    try:
        prior = int(update.message.text)
    except Exception:
        update.message.reply_text("Хочу int, а не вот это вот всё")
        return cancel(update, context)
    context.user_data['prior'] = prior
    update.message.reply_text("Выберите тип: /single_test или /multi_test, или вообще /cancel")
    return ADD_GENERATOR_TYPE_STATE

def add_generator_type(update, context):
    if (update.message.text == "/multi_test"):
        context.user_data['type'] = MULTI_TEST
    elif (update.message.text == "/single_test"):
        context.user_data['type'] = SINGLE_TEST
    else:
        update.message.reply_text("Нужно было нажать на кнопку:(")
        return cancel(update, context)
    update.message.reply_text("Ожидаю файл генератора (или /cancel)")
    return ADD_GENERATOR_FILE_STATE

def add_generator_file(update, context):
    global contest_obj 
    generator_path = os.path.dirname(__file__) + "/contest/generators/" + context.user_data['letter'] + context.user_data['gen_name'] + "_" + gen_timestamp() + ".cpp"
    f = context.bot.getFile(update.message.document.file_id)
    f.download(generator_path) 
    res = contest_obj.add_generator(context.user_data['gen_name'], generator_path, context.user_data['prior'], context.user_data['type'], context.user_data['gen_description'], context.user_data['letter'])
    update.message.reply_text(res[1])
    if (not res[0]):
        os.system("rm " + generator_path)
    return ConversationHandler.END   

ERASE_GENERATOR_LETTER_STATE, ERASE_GENERATOR_NAME_STATE, = range(2)

def erase_generator_entry(update, context):
    update.message.reply_text("Введите заглавную букву задачи(или /cancel)")
    return ADD_GENERATOR_LETTER_STATE

def erase_generator_letter(update, context):
    global contest_obj
    if not len(update.message.text) == 1:
        return cancel(update, context)
    context.user_data['letter'] = update.message.text;
    res = contest_obj.generators_to_string(update.message.text)
    if not res[0]:
        update.message.reply_text(res[1])
        return cancel(update, context)
    update.message.reply_text("Генераторы этой задаче:\n" + "\n".join(res[1]))
    update.message.reply_text("Введите название удаляемого генератора (или /cancel)")
    return ADD_GENERATOR_NAME_STATE
    
def erase_generator_name(update, context):
    global contest_obj 
    res = contest_obj.erase_generator(update.message.text, context.user_data['letter'])
    update.message.reply_text(res[1])
    return ConversationHandler.END

STRESS_LETTER_STATE, STRESS_FILE_STATE, = range(2)

def stress_entry(update, context):
    update.message.reply_text("Введите заглавную букву задачи(или /cancel)")
    return STRESS_LETTER_STATE

def stress_letter(update, context):
    if not len(update.message.text) == 1:
        return cancel(update, context)
    context.user_data['letter'] = update.message.text;
    update.message.reply_text("Ожидаю файл с решением (или /cancel)")
    return STRESS_FILE_STATE   
 
def stress_file(update, context):
    temp_path = os.path.dirname(__file__) + "/temp/" + context.user_data['letter'] + ".cpp"
    f = context.bot.getFile(update.message.document.file_id)
    f.download(temp_path)
    update.message.reply_text("Ok, testing...")
    res = contest_obj.stress(temp_path, context.user_data['letter'])
    os.system("sudo killall -u vitek") # на всякий случай убъём витьков
    update.message.reply_text(res[1])
    context.bot.send_message(int(ADMIN_ID), res[1]) # feedback
    if (res[0]):
        update.message.reply_document(
            open(res[2], 'rb'), 
            filename="test.txt",
            caption="Here is the test, where your program fails:)"
        )
        os.system("rm " + res[2])
        if (res[3] != None):
            if (os.path.isfile(res[3]) and os.path.getsize(res[3]) > 0):
                update.message.reply_document(
                    open(res[3], 'rb'), 
                    filename="right_answer.txt",
                    caption="Right answer on this test."
                )
            else:
                update.message.reply_text("Right answer is empty file")
            os.system("rm " + res[3])
    os.system("rm " + temp_path)
    os.system("sudo rm -f mipt_algobot/temp/user/*")
    return ConversationHandler.END

REPORT_TEXT_STATE = 0

def report_entry(update, context):
    return ConversationHandler.END
    # update.message.reply_text("Введите текст репорта. Например: [нужен генератор по задаче С] или [тесты по задаче А - слабые] (или /cancel)")
    # return REPORT_TEXT_STATE

def report_text(update, context): # by feedback
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text("Диалог окончен, вводите новую команду")
    return ConversationHandler.END

def kill(update, context):
    update.message.reply_text("Сессия закрыта, пока:)")
    os.system(f"rm {os.path.dirname(__file__)}/temp/*")
    quit()

def error(update, context):
    logger.warning('ERROR: Update "%s" caused error "%s"', update, context.error)
    try:
        update.message.reply_text("Error has been occured!")
        context.bot.send_message(int(ADMIN_ID), "Error!")
        context.bot.send_message(int(ADMIN_ID), str(update))
        context.bot.send_message(int(ADMIN_ID), str(context.error))
    except Exception as ex:
        context.bot.send_message(int(ADMIN_ID), "Strange error: " + str(context.error))

# ============ ADDING HANDLERS ==============
def main():
    updater = Updater(BOT_KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", help_text))
    dp.add_handler(CommandHandler("help", help_text))
    dp.add_handler(CommandHandler("guide", guide))
    dp.add_handler(CommandHandler("rules", rules))
    dp.add_handler(CommandHandler("get_id", get_id))
    dp.add_handler(CommandHandler("contest", contest_info))
    dp.add_handler(CommandHandler("managers", get_managers))
    dp.add_handler(CommandHandler("kill", kill))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('add_manager', add_manager_entry)],
        states={
            TYPING_ID_STATE: [
                MessageHandler(Filters.text, add_manager)
            ]
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('erase_manager', erase_manager_entry)],
        states={
            TYPING_ID_STATE: [
                MessageHandler(Filters.text, erase_manager)
            ]
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('set_contest', set_contest_entry)],
        states={
            TYPING_CONTESTSIZE_STATE: [
                MessageHandler(Filters.text, set_contest_size)
            ],
            TYPING_CONTESTLINK_STATE: [
                MessageHandler(Filters.text, set_contest_link)
            ]
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('set_tl', set_timelimit_entry)],
        states={
            TYPING_TIMELIMIT_LETTER_STATE: [
                MessageHandler(Filters.text, set_timelimit_letter)
            ],
            TYPING_TIMELIMIT_VALUE_STATE: [
                MessageHandler(Filters.text, set_timelimit_value)
            ]
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('set_solution', set_solution_entry)],
        states={
            SOLUTION_LETTER_STATE: [
                MessageHandler(Filters.text, set_solution_letter)
            ],
            SOLUTION_FILE_STATE: [
                MessageHandler(Filters.document, set_solution_file)
            ]
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('set_comparator', set_comparator_entry)],
        states={
            COMPARATOR_LETTER_STATE: [
                MessageHandler(Filters.text, set_comparator_letter)
            ],
            COMPARATOR_FILE_STATE: [
                MessageHandler(Filters.document, set_comparator_file),
                CommandHandler('default', set_comparator_default)
            ]
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('add_generator', add_generator_entry)],
        states={
            ADD_GENERATOR_LETTER_STATE: [
                MessageHandler(Filters.text, add_generator_letter)
            ],
            ADD_GENERATOR_NAME_STATE: [
                MessageHandler(Filters.text, add_generator_name)
            ],
            ADD_GENERATOR_DESCRIPTION_STATE: [
                MessageHandler(Filters.text, add_generator_description)
            ],
            ADD_GENERATOR_PRIORITY_STATE: [
                MessageHandler(Filters.text, add_generator_priority)
            ],
            ADD_GENERATOR_TYPE_STATE: [
                CommandHandler("single_test", add_generator_type),
                CommandHandler("multi_test", add_generator_type)
            ],
            ADD_GENERATOR_FILE_STATE: [
                MessageHandler(Filters.document, add_generator_file)
            ],
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('erase_generator', erase_generator_entry)],
        states={
            ERASE_GENERATOR_LETTER_STATE: [
                MessageHandler(Filters.text, erase_generator_letter)
            ],
            ERASE_GENERATOR_NAME_STATE: [
                MessageHandler(Filters.text, erase_generator_name)
            ],
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('stress', stress_entry)],
        states={
            STRESS_LETTER_STATE: [
                MessageHandler(Filters.text, stress_letter)
            ],
            STRESS_FILE_STATE: [
                MessageHandler(Filters.document, stress_file)
            ],
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('report', report_entry)],
        states={
            REPORT_TEXT_STATE: [
                MessageHandler(Filters.text, report_text)
            ],
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    ))
    dp.add_error_handler(error) 
    updater.start_polling()
    updater.idle()

# =============== SETTING UP GLOBAL VARIABLES =================

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

contest_path = os.path.dirname(__file__) + "/contest/contest.txt"
contest_obj = contest()
try:
    contest_obj.load(contest_path)
except Exception as e:
    print(e)

manager_path = os.path.dirname(__file__) + "/contest/access_manager.txt"
access_manager_obj = access_manager()
try:
    access_manager_obj.load(manager_path)
except Exception as e: 
    print(e)
access_manager_obj.set_status(ADMIN_ID, CHIEF_MANAGER)

# =============== SETTING UP PERMISSIONS ================

permissions = { USER :          [help_text, guide, get_id, cancel, stress_entry, report_entry],
                MANAGER :       [help_text, guide,  get_id, cancel, stress_entry, report_entry,
                                rules, set_solution_entry, add_generator_entry, erase_generator_entry, set_timelimit_entry, set_comparator_entry],
                CHIEF_MANAGER:  [help_text, guide, get_id, cancel, stress_entry, report_entry,
                                rules, set_solution_entry, add_generator_entry, erase_generator_entry, set_timelimit_entry, set_comparator_entry,
                                add_manager_entry, erase_manager_entry, get_managers, set_contest_entry, kill]
}

# =============== USING DECORATORS ==================

help_text = access_decorator(help_text)
guide = access_decorator(guide)
get_id = access_decorator(get_id)
rules = access_decorator(rules)
get_managers = access_decorator(get_managers)
cancel = access_decorator(cancel)
kill = access_decorator(kill)

add_manager_entry = access_decorator(add_manager_entry)
add_manager = cancel_decorator(add_manager)

erase_manager_entry = access_decorator(erase_manager_entry)
erase_manager = cancel_decorator(erase_manager)

set_contest_entry = access_decorator(set_contest_entry)
set_contest_size = cancel_decorator(set_contest_size)
set_contest_link = cancel_decorator(set_contest_link)

set_timelimit_entry = access_decorator(set_timelimit_entry)
set_timelimit_letter = cancel_decorator(set_timelimit_letter)
set_timelimit_value = cancel_decorator(set_timelimit_value)

set_solution_entry = access_decorator(set_solution_entry)
set_solution_letter = cancel_decorator(set_solution_letter)
set_solution_file = cancel_decorator(set_solution_file)

set_comparator_entry = access_decorator(set_comparator_entry)
set_comparator_letter = cancel_decorator(set_comparator_letter)
set_comparator_file = cancel_decorator(set_comparator_file)
set_comparator_default = cancel_decorator(set_comparator_default)

add_generator_entry = access_decorator(add_generator_entry)
add_generator_letter = cancel_decorator(add_generator_letter)
add_generator_name = cancel_decorator(add_generator_name)
add_generator_description = cancel_decorator(add_generator_description)
add_generator_priority = cancel_decorator(add_generator_priority)
add_generator_type = cancel_decorator(add_generator_type)
add_generator_file = cancel_decorator(add_generator_file)

erase_generator_entry = access_decorator(erase_generator_entry)
erase_generator_letter = cancel_decorator(erase_generator_letter)
erase_generator_name = cancel_decorator(erase_generator_name)

stress_entry = access_decorator(stress_entry)
stress_letter = cancel_decorator(feedback_decorator(stress_letter))
stress_file = cancel_decorator(stress_file)

report_entry = access_decorator(report_entry)
report_text = cancel_decorator(feedback_decorator(report_text))

# ============== LAUNCH ===============

if __name__ == '__main__':
    main()
