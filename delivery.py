def send_message(msg, update, keyboard=None):
    """
    Send telegram message
    """
    update.message.reply_text(text=msg, parse_mode='HTML', reply_markup=keyboard)


def send_picture(update, picture):
    """
    Send telegram picture
    """
    update.message.reply_photo(photo=picture)


def send_document(update, document):
    """
    Send telegram document
    """
    update.message.reply_document(document=document)


def send_message_object(chat_id, telegram, msg):
    """
    Send telegram message but now using the Telegram object
    """
    telegram.updater.bot.send_message(chat_id=chat_id, text=msg)
