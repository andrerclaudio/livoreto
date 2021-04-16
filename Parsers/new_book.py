# Build-in modules
import logging
import time

# Added modules
import isbnlib

# Project modules
from delivery import send_message

logger = logging.getLogger(__name__)


def isbn_lookup(isbnlike, good_reads):
    """
    Fetch in Good Reads for a given ISBN code
    """
    book_info = {}

    val = [c for c in isbnlike if c.isdigit()]
    isbn = ''.join(val)

    if isbnlib.is_isbn10(val):
        isbn = isbnlib.to_isbn13(val)

    if isbnlib.is_isbn13(isbn):
        try:
            book = good_reads.book(isbn=isbn)

            publisher = book.publisher if book.publisher is not None else '-'
            pages_qty = book.num_pages if book.num_pages is not None else int(0)

            book_info.update({'Título': book.title,
                              'Autor': str(book.authors[0]),
                              'Editora': publisher,
                              'ISBN-13': isbn,
                              'Qtd. de Páginas': pages_qty,
                              'Link': book.link
                              })
        except Exception as e:
            logger.exception('{}'.format(e), exc_info=False)
        finally:
            return book_info
    else:
        return book_info


def book_descriptor(update, book_info):
    """
    Show book info
    """
    msg = ['<i><b>{}</b></i>: {}\n'.format(value, key) for value, key in book_info.items()]
    send_message(''.join(msg), update)


def save_book(update, book_info, database):
    """
    Save book in a database file
    """

    new_book = True
    df = database.get('tREADING')

    if df is not None:
        for book in df:
            if book['ISBN'] == book_info['ISBN-13']:
                new_book = False

    if new_book:
        today = int(time.time())

        df = {'BOOK': book_info['Título'],
              'AUTHOR': book_info['Autor'],
              'PUBLISHER': book_info['Editora'],
              'ISBN': book_info['ISBN-13'],
              'START': today,
              'FINISH': '-',
              'QTY': int(book_info['Qtd. de Páginas']),
              'PRED': '-',
              }

        database.save_data('tREADING', df)
        send_message('Excelente, você começou a ler mais um livro!\n'
                     'Vá em <i><b>"Leituras em andamento"</b></i> para ver detalhes e outras informações', update)
    else:
        send_message('Você já está lendo este livro.\n'
                     'Se deseja adicioná-lo novamente e recomeçar a leitura, primeiro você deve abandonar '
                     'esta leitura dentro de <i><b>"Leituras em andamento"</b></i>!', update)
