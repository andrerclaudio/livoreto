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

DATA_INDEX = 0
MSG_INDEX = 1


class CallBackDataList(object):
    """A simple organization of all possible callback incoming data"""

    def __init__(self):
        self.CHAR_SEPARATOR = '@'
        self.READING = 'current books'
        self.HISTORY_YEARS = 'years list'


def data_callback_parser(query, updater, database, good_reads):
    """

    """
    callback_data_list = CallBackDataList()
    chat_id = str(query.from_user['id'])
    string = str(query.data).split(callback_data_list.CHAR_SEPARATOR)
    data = string[DATA_INDEX]
    msg = string[MSG_INDEX]

    if data == callback_data_list.READING:

        data = database.get('tREADING')
        if data is not None:
            df = pd.DataFrame(data)
            filtered = df.loc[df['ISBN'] == msg]

            start_day = datetime.fromtimestamp(filtered['START'])

            book_info = isbn_lookup(msg, good_reads)
            # Check for a valid information
            if len(book_info) > 0:
                msg = ['<i><b>{}</b></i>: {}\n'.format(value, key) for value, key in book_info.items()]
                # Show book information
                send_message_object(chat_id, updater, ''.join(msg))

                day = start_day.day
                month = start_day.month
                msg = '{} {}'.format(day, month)
                send_message_object(chat_id, updater, msg)

    elif data == callback_data_list.HISTORY_YEARS:

        df = database.get('tHISTORY')
        if df is not None:
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
                book_info = isbn_lookup(isbn, good_reads)
                if len(book_info) > 0:
                    send_message_object(chat_id, updater, book_info['Link'])
