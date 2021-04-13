# Build-in modules
import logging
from collections import Counter
from datetime import datetime

# Added modules
import pandas as pd

# Project modules
from Parsers.new_book import isbn_lookup
from delivery import send_message_object

logger = logging.getLogger(__name__)

PARSER = 0
MSG = 1


def data_callback_parser(query, updater, database):
    """

    """
    data = str(query.data).split('@')
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
                        send_message_object(chat_id, updater, ''.join(msg))

    elif command == 'year_list':

        df = database.get('tHISTORY')
        if df is not None:
            chat_id = str(query.from_user['id'])
            selected_year = msg
            years = [str(datetime.fromtimestamp(data['FINISH']).year) for data in df]
            values = Counter(years)
            qty = values[selected_year]
            msg = 'Você leu <i><b>{}</b></i> livros em <i><b>{}</b></i>.'.format(qty, selected_year)
            send_message_object(chat_id, updater, msg)

            remove_indices = []
            idx = 0
            for y in years:
                if y != selected_year:
                    remove_indices.append(idx)
                idx += 1

            data = [i for j, i in enumerate(df) if j not in remove_indices]
            df = pd.DataFrame(data)

            pages = df['QTY'].sum()
            msg = 'Você leu <i><b>{}</b></i> páginas em <i><b>{}</b></i>.'.format(pages, selected_year)
            send_message_object(chat_id, updater, msg)

            isbn_list = df['ISBN'].tolist()
            for isbn in isbn_list:
                book_info = isbn_lookup(isbn)
                if len(book_info) > 0:
                    send_message_object(chat_id, updater, book_info['Link'])
