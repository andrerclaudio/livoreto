# Added modules
from telegram import InlineKeyboardButton, KeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup

# Project modules
from delivery import send_message as send

MAIN_MENU_KEYBOARD = [[KeyboardButton('Leituras em andamento')],
                      [KeyboardButton('Adicionar um novo livro'),
                       KeyboardButton('Recomendações')]]

BOOK_NAME = 0
BOOK_ISBN = 1


def mount_inline_keyboard(fields):
    """
    Mount a inline keyboard
    """

    sub = []
    keyboard = []

    for book in fields:
        sub.append((InlineKeyboardButton(book[BOOK_NAME], callback_data='{}'.format(book[BOOK_ISBN]))))
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
