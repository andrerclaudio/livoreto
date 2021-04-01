# Build-in modules
import logging

# Added modules
import isbnlib

# Project modules
from Book.client import good_reads_client as good_reads

logger = logging.getLogger(__name__)


def isbn_lookup(isbn):
    """
    Fetch in Good Reads for a given ISBN code
    """
    book_info = {}
    isbn = isbnlib.to_isbn13(isbn) if isbnlib.is_isbn10(isbn) else isbn

    if isbnlib.is_isbn13(isbn):
        try:
            book = good_reads.book(isbn=isbn)

            publisher = book.publisher if book.publisher is not None else '-'
            cover = book.format if book.format is not None else '-'
            language = str(book.language_code).capitalize() if book.language_code is not None else '-'

            book_info.update({'Title': book.title,
                              'Author': str(book.authors[0]),
                              'Publisher': publisher,
                              'Cover': cover,
                              'Language': language,
                              'ISBN-13': isbn,
                              'Link': book.link
                              })
        except Exception as e:
            logger.exception('{}'.format(e), exc_info=False)
        finally:
            return book_info

# def show_book_info(update, book_info):
#     """
#     Show book info
#     """
#     msg = ['<i><b>{}</b></i>: {}\n'.format(value, key) for value, key in book_info.items()]
#     send(''.join(msg), update)


# def save_book_info(update, book_info, database):
#     """
#     Save book in database file
#     """
#     df = database.get_value('tREADING')
#     # Checking is there no table information but headers.
#     if df is not None:
#         send('There is another on going reading! Please, finish it before starting a new book!', update)
#         return False
#     else:
#         # Save book info at database
#         book = book_info['Title']
#         author = book_info['Author']
#         publisher = book_info['Publisher']
#         publication_date = '-'
#         edition = '-'
#         book_cover = book_info['Cover']
#         language = book_info['Language']
#         genre = '-'
#         isbn = book_info['ISBN-13']
#         remark = '-'
#
#         df = {'BOOK': book,
#               'AUTHOR': author,
#               'PUBLISHER': publisher,
#               'PUBLICATION_DATE': publication_date,
#               'EDITION': edition,
#               'BOOK_COVER': book_cover,
#               'LANGUAGE': language,
#               'GENRE': genre,
#               'ISBN': isbn,
#               'REMARK': remark,
#               'START_PAGE': int(0),
#               'END_PAGE': int(0),
#               'START_DAY': int(0),
#               'END_DAY': int(0),
#               'PAGE': int(0),
#               'BOOK_PAGE': int(0),
#               'TIMESTAMP': int(0)
#               }
#
#         database.add_information('tREADING', df)
#         book_info.clear()
#         start_day = int(time.time())
#
#         # Add 0 to table pages at same time it adds a new book
#         df = database.get_value('tPAGES')
#         if df is not None:
#             today = datetime.datetime.today()
#             date = datetime.datetime.fromtimestamp(df['TIMESTAMP'][df.index[-1]])
#             if today.date() != date.date():
#                 # create a new row with the quantity of that day
#                 df = df.append({'QUANTITY': 0, 'TIMESTAMP': start_day}, ignore_index=True)
#         else:
#             # create a new row with the quantity of that day
#             df = {'QUANTITY': 0,
#                   'TIMESTAMP': start_day}
#
#         database.add_information('tPAGES', df)
#
#         send('Great! You have started a new book!', update)
#         return True
