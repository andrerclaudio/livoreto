# Added modules
from telegram import InlineKeyboardButton, KeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup

# Project modules
from delivery import send_message as send

MAIN_MENU_KEYBOARD = [[KeyboardButton('📖 Leituras em andamento 📖')],
                      [KeyboardButton('📚 Adicionar um novo livro'),
                       KeyboardButton('📋 Números')]]

BOOK_NAME = 0
BOOK_ISBN = 1

YEAR_DESCRIPTOR = 0
YEAR_MSG = 1


def mount_inline_keyboard(fields, parser):
    """
    Mount an inline keyboard
    """

    sub = []
    keyboard = []

    if parser == 'reading':
        for book in fields:
            sub.append(
                InlineKeyboardButton(book[BOOK_NAME], callback_data='{}'.format(parser + '@' + str(book[BOOK_ISBN]))))
            keyboard.append(sub.copy())
            sub.clear()
    elif parser == 'year_list':
        for years in fields:
            sub.append(InlineKeyboardButton(years[YEAR_DESCRIPTOR],
                                            callback_data='{}'.format(parser + '@' + str(years[YEAR_MSG]))))
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
