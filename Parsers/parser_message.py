# Build-in modules
import logging
from datetime import datetime

# Project modules
from Parsers.new_book import isbn_lookup, book_descriptor, save_book
from delivery import send_picture, send_message
from menus import add_keyboard, MAIN_MENU_KEYBOARD, mount_inline_keyboard
from settings import settings

# Added modules


logger = logging.getLogger(__name__)


def messages_parser(update, database):
    """
    Incoming message parser
    """

    # Commands
    command_start = ['/start']

    # Buttons
    button_new_book = [' adicionar um novo livro']
    button_reading = [' leituras em andamento ']
    button_numbers = [' números']

    raw = update.message.text
    msg = ''.join(c for c in raw if c not in settings.emoji_list)
    msg = msg.lower()

    # --------------------------------------------------------------------------------------------------------------
    if msg in command_start:
        """
        Show an welcome message.
        """
        send_picture(update, open('Pictures/welcome_pic.jpg', 'rb'))

        msg = 'Olá, amigo leitor!\n' \
              'Clique em <i><b>"Adicionar um novo livro"</b></i> para que possamos começar!\n'

        # Start the main menu
        add_keyboard(update, msg, MAIN_MENU_KEYBOARD)
    # --------------------------------------------------------------------------------------------------------------
    elif msg in button_new_book:
        """
        Tell the user about ISBN value.
        """
        send_message('Digite o código ISBN do livro que vai ler!\n'
                     'Você deve encontrá-lo no final do livro.', update)

        send_message('No exemplo abaixo, seria    <i><b>9788535933925</b></i>\n', update)

        send_picture(update, open('Pictures/isbn.jpeg', 'rb'))
    # --------------------------------------------------------------------------------------------------------------
    elif msg in button_reading:
        df = database.get('tREADING')
        if df is not None:
            books = [(book['BOOK'], book['ISBN']) for book in df]
            command = 'reading'
            keyboard = mount_inline_keyboard(books, command)
            send_message('<i><b>Escolha um livro abaixo para mais detalhes ...</b></i>', update, keyboard)
        else:
            send_message('Nenhuma leitura em andamento! 🙄', update)
    # --------------------------------------------------------------------------------------------------------------
    elif msg in button_numbers:
        df = database.get('tHISTORY')
        if df is not None:
            years_list = [datetime.fromtimestamp(data['FINISH']).year for data in df]
            years_list = list(set(years_list))
            data = [(str(year), str(year)) for year in years_list]
            command = 'year_list'
            keyboard = mount_inline_keyboard(data, command)
            send_message('<i><b>Escolha uma das opções abaixo ...</b></i>', update, keyboard)
        else:
            send_message('Eu ainda não tenho alguns números para te mostrar! 🙄', update)
    # --------------------------------------------------------------------------------------------------------------
    else:
        # ISBN related functions
        book_info = isbn_lookup(msg)
        # Check for a valid information
        if len(book_info) > 0:
            # Show book information
            book_descriptor(update, book_info)
            # Save book info into the user Database
            save_book(update, book_info, database)
        else:
            send_message('Não encontrei o livro.\n'
                         'Por favor, confirme o código ISBN digitado e tente novamente!', update)
