# Build-in modules
import logging

# Project modules
from Parsers.new_book import isbn_lookup
from delivery import send_message_object

# Added modules


logger = logging.getLogger(__name__)


def data_callback_parser(update, telegram_obj, database):
    """

    """
    df = database.get('tREADING')
    query = update.callback_query

    if df is not None:
        for book in df:
            isbn = book['ISBN']
            if str(query.data) == isbn:

                book_info = isbn_lookup(isbn)
                # Check for a valid information
                if len(book_info) > 0:
                    chat_id = str(query.from_user['id'])
                    msg = ['<i><b>{}</b></i>: {}\n'.format(value, key) for value, key in book_info.items()]
                    # Show book information
                    send_message_object(chat_id, telegram_obj, ''.join(msg))
