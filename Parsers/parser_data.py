# Build-in modules
import logging
import random
import time
from collections import Counter
from datetime import datetime

import pandas as pd

# Project modules
from Parsers.new_book import isbn_lookup
from delivery import send_message_object
from menus import mount_inline_keyboard, CallBackDataList

# Added modules

logger = logging.getLogger(__name__)

DATA_INDEX = 0
MSG_INDEX = 1
INFO_INDEX = 2

NUMBER_OF_BOOKS_TO_SHOW_USERS_READING = 8
NUMBER_OF_AUTHORS_TO_SHOW = 8

MONTH_NAMES_PT_BR = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro',
                     'Outubro', 'Novembro', 'Dezembro']

READING_OPTIONS_LEAVE_CURRENT_READING = 'Abandonar a leitura'
READING_OPTIONS_FINISH_CURRENT_READING = 'Leitura finalizada'

COMMUNITY_OTHERS_USERS_READING = '- O que os outros usuários estão lendo.'
COMMUNITY_POPULAR_AUTHORS = '- Autores mais populares.'


def data_callback_parser(query, updater, database, good_reads):
    """
    Parse all data from inline buttons.
    """
    callback_data_list = CallBackDataList()
    chat_id = str(query.from_user['id'])
    string = str(query.data).split(callback_data_list.CHAR_SEPARATOR)

    data = string[DATA_INDEX]
    msg = string[MSG_INDEX]

    if data == callback_data_list.READING:

        data = database.get('tREADING')
        df = pd.DataFrame(data)
        isbn = msg
        filtered = df.loc[df['ISBN'] == isbn]

        start_day = datetime.fromtimestamp(filtered['START'])

        book_info = isbn_lookup(isbn, good_reads)
        # Check for a valid information
        if len(book_info) > 0:

            if book_info['Qtd. de Páginas'] == 0:
                book_info['Qtd. de Páginas'] = '-'

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
                    msg = 'Você abandonou o livro! 🙄'
                    send_message_object(chat_id, updater, msg)
                    database.drop_document('tREADING', doc_id)
                    break

    elif data == callback_data_list.COMMUNITY:

        # Close current database
        database.disconnect(server_close=False)

        db_list = database.client.list_database_names()
        db_list.remove('admin')
        db_list.remove('local')

        if msg == COMMUNITY_OTHERS_USERS_READING:
            all_users_reading = []
            for db in db_list:
                # Exclude the person who is logged
                if db != chat_id:
                    # Connect to Database
                    database.connect(db)
                    df = database.get('tREADING')
                    if df is not None:
                        if len(df) > 0:
                            for book in df:
                                book_info = isbn_lookup(book['ISBN'], good_reads)
                                # Check for a valid information
                                if len(book_info) > 0:
                                    all_users_reading.append(book_info['Link'])

                    # Close current database
                    database.disconnect(server_close=False)

            if len(all_users_reading) > 0:
                # To avoid flooding the current users screen
                if len(all_users_reading) > NUMBER_OF_BOOKS_TO_SHOW_USERS_READING:
                    index_to_keep = []
                    total = len(all_users_reading)
                    for i in range(0, NUMBER_OF_BOOKS_TO_SHOW_USERS_READING):
                        index_to_keep.append(random.randint(0, total))

                    data = [i for j, i in enumerate(all_users_reading) if j in index_to_keep]
                    [send_message_object(chat_id, updater, link) for link in data]
                else:
                    [send_message_object(chat_id, updater, link) for link in all_users_reading]
            else:
                send_message_object(chat_id, updater, 'Não temos nenhuma leitura ativa em nossa comunidade. '
                                                      'Que pena! 😒')

        if msg == COMMUNITY_POPULAR_AUTHORS:
            authors = []
            for db in db_list:
                # Connect to Database
                database.connect(db)

                reading = database.get('tREADING')
                if reading is not None:
                    if len(reading) > 0:
                        for name in reading:
                            authors.append(name['AUTHOR'])

                history = database.get('tHISTORY')
                if history is not None:
                    [authors.append(name['AUTHOR']) for name in history]

                # Close current database
                database.disconnect(server_close=False)

            values = Counter(authors)
            authors = sorted(values.items(), key=lambda x: x[1], reverse=True)
            df = pd.DataFrame(authors)
            top_author = df.head(NUMBER_OF_AUTHORS_TO_SHOW)
            for name in top_author[0]:
                try:
                    details = good_reads.find_author(author_name=name)
                    if details is not None:
                        send_message_object(chat_id, updater, details.link)
                except Exception as e:
                    logger.exception('{}'.format(e), exc_info=False)
