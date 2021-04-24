# Build-in modules
import logging
from datetime import datetime

# Project modules
from Parsers.new_book import isbn_lookup, save_book
from Parsers.parser_data import COMMUNITY_OTHERS_USERS_READING, COMMUNITY_POPULAR_AUTHORS
from delivery import send_picture, send_message
from menus import mount_inline_keyboard, CallBackDataList, add_keyboard, MAIN_MENU_KEYBOARD

# Added modules


logger = logging.getLogger(__name__)


def messages_parser(update, database, good_reads):
    """
    Incoming message parser
    """

    # Buttons
    button_new_book = ['📚 Adicionar um novo livro']
    button_reading = ['📖 Leituras em andamento 📖']
    button_numbers = ['📋 Números']
    button_community = ['Comunidade Livoreto']

    msg = update.message.text

    # Load possibles callback data
    callback_data_list = CallBackDataList()

    # --------------------------------------------------------------------------------------------------------------
    if msg in button_new_book:
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
            if len(df) > 0:
                books = [(book['BOOK'], book['ISBN']) for book in df]
                data = callback_data_list.READING
                keyboard = mount_inline_keyboard(books, data)
                send_message('<i><b>Escolha um livro abaixo para mais detalhes ...</b></i>', update, keyboard)
            else:
                send_message('Nenhuma leitura em andamento! 🙄', update)
        else:
            send_message('Nenhuma leitura em andamento! 🙄', update)
    # --------------------------------------------------------------------------------------------------------------
    elif msg in button_numbers:
        df = database.get('tHISTORY')
        if df is not None:
            years_list = [datetime.fromtimestamp(data['FINISH']).year for data in df]
            years_list = list(set(years_list))
            years = [str(year) for year in years_list]
            data = callback_data_list.HISTORY_YEARS
            keyboard = mount_inline_keyboard(years, data)
            send_message('<i><b>Escolha uma das opções abaixo ...</b></i>', update, keyboard)
        else:
            send_message('Eu ainda não tenho números para te mostrar! 🙄', update)
    # --------------------------------------------------------------------------------------------------------------
    elif msg in button_community:
        msg = [COMMUNITY_OTHERS_USERS_READING, COMMUNITY_POPULAR_AUTHORS]
        data = callback_data_list.COMMUNITY
        keyboard = mount_inline_keyboard(msg, data)
        send_message('<i><b>Escolha uma das opções abaixo ...</b></i>', update, keyboard)
    # --------------------------------------------------------------------------------------------------------------
    else:
        # ISBN related functions
        book_info = isbn_lookup(msg, good_reads)
        # Check for a valid information
        if len(book_info) > 0:
            # Save book info into the user Database
            save_book(update, book_info, database)
        else:
            msg = 'Não encontrei o livro.\n' \
                  'Por favor, confirme o código ISBN digitado e tente novamente!'
            # Start the main menu
            add_keyboard(update, msg, MAIN_MENU_KEYBOARD)
