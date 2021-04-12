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


def send_message_object(chat_id, updater, msg, keyboard=None):
    """
    Send telegram message but now using the Telegram object
    """
    updater.bot.send_message(chat_id=chat_id, parse_mode='HTML', text=msg, reply_markup=keyboard)
