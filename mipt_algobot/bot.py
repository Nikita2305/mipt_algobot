import logging
import os
from mipt_algobot.contest import *
from mipt_algobot.access_manager import *
from functools import wraps

ADMIN_ID = "???"
BOT_KEY = "???"

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
            return (False, "Access decorator forbids")
        ret = function(update, context)
        dump_system()
        return ret
    return decorated

def help_text(update, context):
    update.message.reply_text(
    """
+ /help - to see this message

*For users*
+ /contest\_info
+ /get\_id
+ /stress
+ /cancel

*For managers*
+ /rules
+ /set\_contest
+ /set\_solution
+ /add\_generator
+ /erase\_generator

*For chief manager*
+ /add\_manager
+ /erase\_manager
+ /managers
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
    contest_obj = contest(context.user_data['size'], update.message.text)
    update.message.reply_text("Создан контест на " + str(context.user_data['size']) +" задач")
    return ConversationHandler.END

def contest_info(update, context):
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
    solution_path = "./mipt_algobot/contest/solutions/" + context.user_data['letter'] + str(update.effective_user.id) + ".cpp"
    f = context.bot.getFile(update.message.document.file_id)
    f.download(solution_path)
    res = contest_obj.set_solution(solution_path, context.user_data['letter'])
    update.message.reply_text(res[1])
    return ConversationHandler.END 

ADD_GENERATOR_LETTER_STATE, ADD_GENERATOR_NAME_STATE, ADD_GENERATOR_FILE_STATE, = range(3)

def add_generator_entry(update, context):
    update.message.reply_text("Введите заглавную букву задачи(или /cancel)")
    return ADD_GENERATOR_LETTER_STATE

def add_generator_letter(update, context):
    global contest_obj
    if not len(update.message.text) == 1:
        return cancel(update, context)
    context.user_data['letter'] = update.message.text;
    res = contest_obj.generators_names(update.message.text)
    if not res[0]:
        update.message.reply_text(res[1])
        return cancel(update, context)
    update.message.reply_text("Генераторы этой задаче:\n" + "\n".join(res[1]))
    update.message.reply_text("Введите название вашего генератора (или /cancel)")
    return ADD_GENERATOR_NAME_STATE

def add_generator_name(update, context):
    context.user_data['gen_name'] = update.message.text;
    update.message.reply_text("Ожидаю файл генератора (или /cancel)")
    return ADD_GENERATOR_FILE_STATE

def add_generator_file(update, context):
    global contest_obj
    generator_path = "./mipt_algobot/contest/generators/" + context.user_data['letter'] + context.user_data['gen_name'] + ".cpp"
    f = context.bot.getFile(update.message.document.file_id)
    f.download(generator_path)
    res = contest_obj.add_generator(context.user_data['gen_name'], generator_path, context.user_data['letter'])
    update.message.reply_text(res[1])
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
    res = contest_obj.generators_names(update.message.text)
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
    temp_path = "./mipt_algobot/temp/" + context.user_data['letter'] + ".cpp"
    f = context.bot.getFile(update.message.document.file_id)
    f.download(temp_path)
    update.message.reply_text("Ok, testing...")
    res = contest_obj.stress(temp_path, context.user_data['letter'])
    update.message.reply_text(res[1])
    if (res[0]):
        update.message.reply_document(
            open(res[2], 'rb'), 
            filename="test.txt",
            caption="Here is the test, where your program fails:)"
        )
        os.system("rm " + res[2])
    os.system("rm " + temp_path)
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text("Диалог окончен, вводите новую команду")
    return ConversationHandler.END

def error(update, context):
    logger.warning('ERROR: Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text("Error has been occured!")

# ============ ADDING HANDLERS ==============
def main():
    updater = Updater(BOT_KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", help_text))
    dp.add_handler(CommandHandler("help", help_text))
    dp.add_handler(CommandHandler("rules", rules))
    dp.add_handler(CommandHandler("get_id", get_id))
    dp.add_handler(CommandHandler("contest_info", contest_info))
    dp.add_handler(CommandHandler("managers", get_managers))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('add_manager', add_manager_entry)],
        states={
            TYPING_ID_STATE: [
                MessageHandler(Filters.text, add_manager)
            ]
        },
        fallbacks=[]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('erase_manager', erase_manager_entry)],
        states={
            TYPING_ID_STATE: [
                MessageHandler(Filters.text, erase_manager)
            ]
        },
        fallbacks=[]
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
        fallbacks=[]
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
        entry_points=[CommandHandler('add_generator', add_generator_entry)],
        states={
            ADD_GENERATOR_LETTER_STATE: [
                MessageHandler(Filters.text, add_generator_letter)
            ],
            ADD_GENERATOR_NAME_STATE: [
                MessageHandler(Filters.text, add_generator_name)
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
        fallbacks=[]
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
    dp.add_error_handler(error) 
    updater.start_polling()
    updater.idle()

# =============== SETTING UP GLOBAL VARIABLES =================

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

contest_path = "./mipt_algobot/contest/contest.txt"
contest_obj = contest()
try:
    contest_obj.load(contest_path)
except Exception:
    pass

manager_path = "./mipt_algobot/contest/access_manager.txt"
access_manager_obj = access_manager()
try:
    access_manager_obj.load(manager_path)
except Exception: 
    pass 
access_manager_obj.set_status(ADMIN_ID, CHIEF_MANAGER)

# =============== SETTING UP PERMISSIONS ================

permissions = { USER :          [help_text, get_id, cancel, stress_entry],
                MANAGER :       [help_text, get_id, cancel, stress_entry,
                                rules, set_contest_entry, set_solution_entry, add_generator_entry, erase_generator_entry],
                CHIEF_MANAGER:  [help_text, get_id, cancel, stress_entry,
                                rules, set_contest_entry, set_solution_entry, add_generator_entry, erase_generator_entry,
                                add_manager_entry, erase_manager_entry, get_managers]
}

# =============== USING DECORATORS ==================

help_text = access_decorator(help_text)
get_id = access_decorator(get_id)
rules = access_decorator(rules)
get_managers = access_decorator(get_managers)
cancel = access_decorator(cancel)

add_manager_entry = access_decorator(add_manager_entry)
add_manager = cancel_decorator(add_manager)

erase_manager_entry = access_decorator(erase_manager_entry)
erase_manager = cancel_decorator(erase_manager)

set_contest_entry = access_decorator(set_contest_entry)
set_contest_size = cancel_decorator(set_contest_size)
set_contest_link = cancel_decorator(set_contest_link)

set_solution_entry = access_decorator(set_solution_entry)
set_solution_letter = cancel_decorator(set_solution_letter)
set_solution_file = cancel_decorator(set_solution_file)

add_generator_entry = access_decorator(add_generator_entry)
add_generator_letter = cancel_decorator(add_generator_letter)
add_generator_name = cancel_decorator(add_generator_name)
add_generator_file = cancel_decorator(add_generator_file)

erase_generator_entry = access_decorator(erase_generator_entry)
erase_generator_letter = cancel_decorator(erase_generator_letter)
erase_generator_name = cancel_decorator(erase_generator_name)

stress_entry = access_decorator(stress_entry)
stress_letter = cancel_decorator(stress_letter)
stress_file = cancel_decorator(stress_file)

# ============== LAUNCH ===============

if __name__ == '__main__':
    main()
