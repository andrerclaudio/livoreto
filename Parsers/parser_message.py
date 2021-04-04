# Build-in modules
import logging

# Project modules
from Parsers.new_book import isbn_lookup, book_descriptor, save_book
from delivery import send_picture, send_message
from menus import add_keyboard, MAIN_MENU_KEYBOARD, mount_keyboard

# Added modules


logger = logging.getLogger(__name__)


def messages_parser(update, database):
    """
    Incoming message parser
    """

    # Commands
    command_start = ['/start']

    # Buttons
    button_new_book = ['adicionar um novo livro']
    button_reading = ['leituras em andamento']
    button_back = ['voltar']

    msg = str(update.message.text)
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

        send_picture(update, open('Pictures/isbn.jpeg', 'rb'))

        send_message('Neste exemplo seria: <i><b>9788535933925</b></i>\n', update)
    # --------------------------------------------------------------------------------------------------------------
    elif msg in button_reading:
        df = database.get('tREADING')

        if df is not None:
            books = [book['BOOK'] for book in df]
            keyboard = mount_keyboard(books)
            add_keyboard(update, 'Veja as leituras em andamento e outras.', keyboard)
        else:
            send_message('Nao tem nenhum livro cadastrado! =/', update)
    # --------------------------------------------------------------------------------------------------------------
    elif msg in button_back:
        add_keyboard(update, 'Escolha uma das opcoes para continuar!', MAIN_MENU_KEYBOARD)
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
