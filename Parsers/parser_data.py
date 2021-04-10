# Build-in modules
import logging
from collections import Counter
from datetime import datetime

# Project modules
from Parsers.new_book import isbn_lookup
from delivery import send_message_object

# Added modules


logger = logging.getLogger(__name__)

PARSER = 0
MSG = 1


def data_callback_parser(update, telegram_obj, database):
    """

    """
    query = update.callback_query
    data = str(query.data)
    data = data.split('@')
    command = data[PARSER]
    msg = data[MSG]

    if command == 'reading':

        df = database.get('tREADING')
        if df is not None:
            for book in df:
                isbn = book['ISBN']
                if msg == isbn:

                    book_info = isbn_lookup(isbn)
                    # Check for a valid information
                    if len(book_info) > 0:
                        chat_id = str(query.from_user['id'])
                        msg = ['<i><b>{}</b></i>: {}\n'.format(value, key) for value, key in book_info.items()]
                        # Show book information
                        send_message_object(chat_id, telegram_obj, ''.join(msg))

    elif command == 'year_list':

        df = database.get('tHISTORY')
        if df is not None:
            chat_id = str(query.from_user['id'])
            selected_year = msg
            years = [str(datetime.fromtimestamp(data['FINISH']).year) for data in df]
            values = Counter(years)
            qty = values[selected_year]
            msg = 'Você leu <i><b>{}</b></i> em <i><b>{}</b></i>.'.format(qty, msg)
            send_message_object(chat_id, telegram_obj, msg)

            remove_indices = []
            idx = 0
            for y in years:
                if y != selected_year:
                    remove_indices.append(idx)
                idx += 1

            df = [i for j, i in enumerate(df) if j not in remove_indices]
            isbn_list = [data['ISBN'] for data in df]

            for isbn in isbn_list:
                book_info = isbn_lookup(isbn)
                if len(book_info) > 0:
                    send_message_object(chat_id, telegram_obj, book_info['Link'])
