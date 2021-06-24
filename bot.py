from botToken import *
import telebot
import os
from telebot import types
from datetime import datetime

USERS_FILE_NAME = "users.txt"       # name it what you want
HELLO_MESSAGE_FILE = 'hello.txt'
FILE_LIST_FILE_NAME = 'loadedFiles.txt'
LOADED_FILES_LIST = {}
LOADED_FILES_INDEX_LIST = {}
USERS_LIST = {}  # debug info
ADMIN_LIST = ['Novarely', 'nata_petrash']

LOG_FILE_NAME = 'eventsLog'
LOG_FILE_FORMAT = '.log'
LOG_FILE = LOG_FILE_NAME + LOG_FILE_FORMAT
LOG_MAX_FILE_SIZE = 1073741824
LOG_TYPE_WARNING    = '[WARNING]'
LOG_TYPE_ERROR      = '[ERROR]  '
LOG_TYPE_INFO       = '[INFO]   '

def log(type, user, command, message = ''):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if os.path.isfile(LOG_FILE) and os.path.getsize(LOG_FILE) > LOG_MAX_FILE_SIZE:
        new_log_file_name = LOG_FILE_NAME + '_' + current_time + LOG_FILE_FORMAT
        os.rename(LOG_FILE, new_log_file_name+LOG_FILE_FORMAT)
    with open(LOG_FILE, 'a') as out:
        log_message = "{}{} => {}. {}".format(type, current_time, user, command)
        if message:
            log_message = log_message + '. {}'.format(message)
        out.write(log_message + "\n")
        print(log_message)
        out.close()

def is_admin(message):
    log(LOG_TYPE_INFO, message.from_user.username, 'is_admin', 'Check is user admin')
    if message.from_user.username in ADMIN_LIST:
        return True
    return False

def write_users_from_file():
    try:
        with open(USERS_FILE_NAME) as inp:
            for i in inp.readlines():
                key, val = i.strip().split(':')
                USERS_LIST[key] = val
            inp.close()
    except FileNotFoundError:
        with open(USERS_FILE_NAME, 'w') as out:
            for key, val in USERS_LIST.items():
                out.write('{}:{}\n'.format(key, val))
            out.close()

def add_user_to_list(message):
    global USERS_LIST
    log(LOG_TYPE_INFO, message.from_user.username, 'add_user_to_list', 'adding user')
    if not USERS_LIST.get(str(message.chat.id)):
        USERS_LIST[str(message.chat.id)] = str(message.from_user.username)
        with open(USERS_FILE_NAME, 'w') as out:
            for key, val in USERS_LIST.items():
                out.write('{}:{}\n'.format(key, val))
            out.close()
        log(LOG_TYPE_INFO, message.from_user.username, 'add_user_to_list', 'user added')

def load_files_on_server():
    try:
        with open(FILE_LIST_FILE_NAME) as inp:
            for i in inp.readlines():
                key, val = i.strip().split('=>')
                LOADED_FILES_LIST[key] = val
            inp.close()
    except FileNotFoundError:
        with open(FILE_LIST_FILE_NAME, 'w') as out:
            for key, val in LOADED_FILES_LIST.items():
                out.write('{}=>{}\n'.format(key, val))
            out.close()

def add_file_to_list(caption, save_dir, file_name):
    global LOADED_FILES_LIST
    LOADED_FILES_LIST[caption.lower()] = save_dir + '/' + file_name
    with open(FILE_LIST_FILE_NAME, 'w') as out:
        for key, val in LOADED_FILES_LIST.items():
            out.write('{}=>{}\n'.format(key, val))
        out.close()

def getHelloMessage():
    hello = ''
    try:
        with open(HELLO_MESSAGE_FILE) as inp:
            for i in inp.readlines():
                hello = hello + i
            inp.close()
    except FileNotFoundError:
        with open(HELLO_MESSAGE_FILE, 'w') as out:
            out.write(hello)
            out.close()
    if not hello:
        hello = 'Default hello message'
    return hello


def getCommandsHelp():
    return "Hi! list of commands\n" \
        + "/start - init the bot (adding user to DB)\n" \
        + "/setHelloMessage {Message} - setting hello message\n" \
        + "/removeKeyboard - removing keyboard\n" \
        + "/getFile - list of all available files to download\n" \
        + "Also you cal load files to bot and he will save them (you need to set Caption to find the file later) \n"

bot = telebot.TeleBot(BOT_TOKEN)
write_users_from_file()

@bot.message_handler(commands=['start'])
def start_command(message):
    log(LOG_TYPE_INFO, message.from_user.username, 'start')

    add_user_to_list(message)
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(types.KeyboardButton('/getFile'))
    markup.add(types.KeyboardButton('/removeKeyboard'))
    markup.add(types.KeyboardButton('/help'))

    if is_admin(message):
        bot.send_message(message.chat.id, 'You are the Admin')
        markup.add(types.KeyboardButton('/setHelloMessage'))
        markup.add(types.KeyboardButton('/removeFile'))

    bot.send_message(message.chat.id, getHelloMessage(), reply_markup=markup)

@bot.message_handler(commands=['help'])
def help(message):
    log(LOG_TYPE_INFO, message.from_user.username, 'help')

    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(types.KeyboardButton('/getFile'))
    markup.add(types.KeyboardButton('/removeKeyboard'))
    markup.add(types.KeyboardButton('/help'))

    if is_admin(message):
        bot.send_message(message.chat.id, 'You are the Admin')
        markup.add(types.KeyboardButton('/setHelloMessage'))

    bot.send_message(message.chat.id, getCommandsHelp(), reply_markup=markup)

@bot.message_handler(commands=['removeKeyboard'])
def removeKeyboard(message):
    log(LOG_TYPE_INFO, message.from_user.username, 'removeKeyboard')

    bot.send_message(message.chat.id, 'Removing keyboard', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['removeFile'])
def removeKeyboard(message):
    log(LOG_TYPE_INFO, message.from_user.username, 'removeFile')

    bot.send_message(message.chat.id, 'Removing keyboard', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['setHelloMessage'])
def setHelloMessage(message):
    log(LOG_TYPE_INFO, message.from_user.username, 'setHelloMessage')

    if is_admin(message):
        messageText = message.text.replace('/setHelloMessage', '')
        if messageText:
            with open(HELLO_MESSAGE_FILE, 'w') as out:
                out.write(messageText)
                out.close()
            bot.send_message(message.chat.id, "Message set!")
            log(LOG_TYPE_INFO, message.from_user.username, 'setHelloMessage', 'message updated to' + messageText)
        else:
            bot.send_message(message.chat.id, "Message can't be empty!")
            log(LOG_TYPE_WARNING, message.from_user.username, 'setHelloMessage', "Message can't be empty!")

    else:
        exMessage = "Permission denied! You are not an Admin!"
        bot.send_message(message.chat.id, exMessage)
        log(LOG_TYPE_WARNING, message.from_user.username, 'setHelloMessage', exMessage)

@bot.message_handler(content_types=['document'])
def document(message):
    log(LOG_TYPE_INFO, message.from_user.username, 'document', 'receiving document from user')

    if is_admin(message):
        mess = bot.send_message(message.chat.id, 'Loading...')
        try:
            save_dir = os.getcwd() + '/files'
            if not os.path.isdir(save_dir):
                os.mkdir(save_dir)
            file_name = message.document.file_name
            file_id = str(message.document.file_id)
            file_id_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_id_info.file_path)
            src = file_name

            bot.edit_message_text('writing...', message.chat.id, mess.id)
            log(LOG_TYPE_INFO, message.from_user.username, 'document', 'writing document to folder')

            with open(save_dir + "/" + src, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.edit_message_text("[✅] File added:\nFile name - {}\nFile directory - {}".format(str(file_name), str(save_dir)), message.chat.id, mess.id)
            add_file_to_list(message.caption, save_dir, file_name)
            log(LOG_TYPE_INFO, message.from_user.username, 'document', 'document loaded')

        except Exception as ex:
            bot.send_message(message.chat.id, "[!] error - {}".format(str(ex)))
            log(LOG_TYPE_ERROR, message.from_user.username, 'document', "[!] error - {}".format(str(ex)))


@bot.message_handler(commands=['getFile'])
def get_file(message):
    log(LOG_TYPE_INFO, message.from_user.username, 'getFile')

    load_files_on_server()
    keyboard = types.InlineKeyboardMarkup()
    iterator = 0

    global LOADED_FILES_INDEX_LIST
    if not len(LOADED_FILES_LIST) == len(LOADED_FILES_INDEX_LIST):
        for key, elem in LOADED_FILES_LIST.items():
            iterator += 1
            LOADED_FILES_INDEX_LIST[iterator] = key

    for key, elem in LOADED_FILES_INDEX_LIST.items():
        callback_data = 'getFile=>' + str(key)
        log(LOG_TYPE_INFO, message.from_user.username, 'get file list', elem)
        keyboard.add(types.InlineKeyboardButton(text=elem, callback_data=callback_data))
    if not LOADED_FILES_LIST.items():
        bot.send_message(message.chat.id, 'No available files at the moment...', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Select files to download', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        command = call.data.split('=>')[0]

        if command == 'getFile':
            file_name_i = call.data.split('=>')[1]

            file_name = ''
            try:

                file_name = LOADED_FILES_INDEX_LIST[int(file_name_i)]

                file_path = LOADED_FILES_LIST[file_name]
                file = open(file_path, "rb")
                bot.send_document(call.message.chat.id, file)
                log(LOG_TYPE_INFO, call.message.from_user.username, 'getFile/callback')
            except Exception as ex:
                bot.send_message(call.message.chat.id, str(ex))
                log(LOG_TYPE_ERROR, call.message.from_user.username, 'getFile/callback', '\'File ' + file_name + ' was not found\' exception')

        if command == 'sendToAll':
            if call.data == 'sendToAll':
                for key, val in USERS_LIST.items():
                    bot.send_message(key, call.message.text)
                    log(LOG_TYPE_INFO, call.message.from_user.username, 'sendToAll/callback')

            # elif call.data == 'hideButtons':
            #     call.message.

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if is_admin(message):
        bot.send_message(message.chat.id, 'Remove keyboard', reply_markup=types.ReplyKeyboardRemove())
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Send to all users', callback_data='sendToAll'))

        bot.reply_to(message, message.text, reply_markup=keyboard)
    else:
        bot.reply_to(message, message.text)

bot.polling()
