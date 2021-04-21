# Build-in modules
import logging
import time
from collections import Counter
from datetime import datetime

# Added modules
import pandas as pd

# Project modules
from Parsers.new_book import isbn_lookup
from delivery import send_message_object
from menus import mount_inline_keyboard, CallBackDataList

logger = logging.getLogger(__name__)

DATA_INDEX = 0
MSG_INDEX = 1
INFO_INDEX = 2

MONTH_NAMES_PT_BR = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro',
                     'Outubro', 'Novembro', 'Dezembro']

READING_OPTIONS_LEAVE_CURRENT_READING = 'Abandonar a leitura'
READING_OPTIONS_FINISH_CURRENT_READING = 'Leitura finalizada'


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
            isbn = msg
            filtered = df.loc[df['ISBN'] == isbn]

            start_day = datetime.fromtimestamp(filtered['START'])

            book_info = isbn_lookup(isbn, good_reads)
            # Check for a valid information
            if len(book_info) > 0:

                if book_info['Qtd. de Páginas'] == 0:
                    book_info['Qtd. de Páginas'] = '-'

                book_info['Qtd. de Páginas'] = book_info['Qtd. de Páginas'] + '\n'
                msg = ['<i><b>{}</b></i>: {}\n'.format(value, key) for value, key in book_info.items()]
                # Show book information
                send_message_object(chat_id, updater, ''.join(msg))

                day = start_day.day
                month = MONTH_NAMES_PT_BR[start_day.month]
                delta = (datetime.today() - start_day).days

                if delta == 0:
                    msg = 'Voce começou ele hoje mesmo.\n\n'
                elif delta == 1:
                    msg = 'Voce começou ele ontem.\n\n'
                elif delta > 1:
                    delta = '{:0>2} dias atrás'.format(delta)
                    msg = 'Voce começou ele no dia {:0>2} de {} ({}).\n\n'.format(day, month, delta)

                options = [(READING_OPTIONS_FINISH_CURRENT_READING, isbn),
                           (READING_OPTIONS_LEAVE_CURRENT_READING, isbn)]
                data = callback_data_list.READING_OPTIONS
                keyboard = mount_inline_keyboard(options, data)
                send_message_object(chat_id, updater, msg, keyboard)

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

    elif data == callback_data_list.READING_OPTIONS:
        info = string[INFO_INDEX]
        isbn = msg
        if info == READING_OPTIONS_FINISH_CURRENT_READING:
            df = database.get('tREADING')
            for book in df:
                if book['ISBN'] == isbn:
                    doc_id = book['_id']
                    today = int(time.time())
                    df = {'BOOK': book['BOOK'],
                          'AUTHOR': book['AUTHOR'],
                          'PUBLISHER': book['PUBLISHER'],
                          'ISBN': book['ISBN'],
                          'START': book['START'],
                          'FINISH': today,
                          'QTY': int(book['QTY']),
                          }

                    database.save_data('tHISTORY', df)
                    msg = 'Você finalizou mais um livro. Parabéns! 🥳👏👏💪'
                    send_message_object(chat_id, updater, msg)
                    database.drop_document('tREADING', doc_id)
                    break

        elif info == READING_OPTIONS_LEAVE_CURRENT_READING:
            df = database.get('tREADING')
            for book in df:
                if book['ISBN'] == isbn:
                    doc_id = book['_id']
                    today = int(time.time())
                    df = {'BOOK': book['BOOK'],
                          'AUTHOR': book['AUTHOR'],
                          'PUBLISHER': book['PUBLISHER'],
                          'ISBN': book['ISBN'],
                          'START': book['START'],
                          'DROP': today,
                          'QTY': int(book['QTY']),
                          }

                    database.save_data('tDROPPED', df)
                    msg = 'Você abandonou o livro! 😪😔'
                    send_message_object(chat_id, updater, msg)
                    database.drop_document('tREADING', doc_id)
                    break
