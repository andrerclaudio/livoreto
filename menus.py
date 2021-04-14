# Added modules
from telegram import InlineKeyboardButton, KeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup

# Project modules
from Parsers.parser_data import CallBackDataList
from delivery import send_message as send

MAIN_MENU_KEYBOARD = [[KeyboardButton('📖 Leituras em andamento 📖')],
                      [KeyboardButton('📚 Adicionar um novo livro'),
                       KeyboardButton('📋 Números')]]

BOOK_NAME_INDEX = 0
BOOK_ISBN_INDEX = 1


def mount_inline_keyboard(fields, data):
    """
    Mount an inline keyboard
    """

    sub = []
    keyboard = []

    # Load possibles callback data
    callback_data_list = CallBackDataList()

    if data == callback_data_list.READING:
        for book in fields:
            sub.append(
                InlineKeyboardButton(book[BOOK_NAME_INDEX], callback_data='{}'.format(data +
                                                                                      callback_data_list.CHAR_SEPARATOR
                                                                                      + str(book[BOOK_ISBN_INDEX]))))
            keyboard.append(sub.copy())
            sub.clear()
    elif data == callback_data_list.HISTORY_YEARS:
        for years in fields:
            sub.append(InlineKeyboardButton(years,
                                            callback_data='{}'.format(data + callback_data_list.CHAR_SEPARATOR +
                                                                      years)))
            keyboard.append(sub.copy())
            sub.clear()

    return InlineKeyboardMarkup(keyboard)


def add_keyboard(update, msg, keyboard):
    """
    Add a new keyboard
    """
    reply_kb_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Send the message with the new keyboard
    send(msg, update, reply_kb_markup)


def remove_keyboard(update, msg):
    """
    Remove de current keyboard
    """
    reply_kb_markup = ReplyKeyboardRemove(remove_keyboard=True)

    # Send the message at the same time the keyboard is removed
    send(msg, update, reply_kb_markup)
