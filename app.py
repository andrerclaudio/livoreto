# Build-in modules
import logging
import os
import time
from multiprocessing import cpu_count as cpu
from threading import Thread

from flask import Flask
# Added modules
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler, CommandHandler

# Project modules
from Book.client import GoodReadsClient
from delivery import send_picture
from menus import add_keyboard, MAIN_MENU_KEYBOARD
from system_digest import message_digest, data_digest

# Print in software terminal
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(process)d | %(threadName)s | %(levelname)s: '
                           '%(message)s',
                    datefmt='%d/%b/%Y - %H:%M:%S')

w = Flask(__name__)
logger = logging.getLogger(__name__)


class FunctionalSystemSettings(object):

    def __init__(self, environment):
        # --------------------------------------------------------------------------------
        if environment == 'Heroku':
            self.WORK_MODE = 'production'
        else:
            self.WORK_MODE = 'development'
        # --------------------------------------------------------------------------------
        """
        Recommendations System Settings.
        """
        self.MINUTES = 30
        self.run_at_initialization = True
        self.running_recommender = True
        self.last_recommendation_run = time.time()
        self.DELTA = 60 * self.MINUTES
        # --------------------------------------------------------------------------------


class InitializeTelegram(object):
    """Telegram Bot initializer"""

    def __init__(self, settings, good_reads):
        # Configuring bot

        if settings.WORK_MODE == 'development':
            telegram_token = os.environ['DEV']
        else:
            telegram_token = os.environ['DEFAULT']

        # Connecting to Telegram API
        self.updater = Updater(token=telegram_token, use_context=True)
        dispatcher = self.updater.dispatcher

        # Creating handlers
        start_handler = CommandHandler('start', lambda update, context: start(update))
        data_handler = CallbackQueryHandler(lambda update, context: telegram_data(update, self.updater, good_reads))
        msg_handler = MessageHandler(Filters.text, lambda update, context: telegram_message(update, good_reads))

        # Message handler must be the last one
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(data_handler)
        dispatcher.add_handler(msg_handler)

        # log all errors
        dispatcher.add_error_handler(error)
        if settings.WORK_MODE == 'production':

            self.port = int(os.environ.get('PORT', '80'))
            self.updater.start_webhook(listen="0.0.0.0",
                                       port=self.port,
                                       url_path=telegram_token,
                                       webhook_url="https://livoreto.herokuapp.com/{}".format(telegram_token),
                                       drop_pending_updates=True,
                                       )
        else:
            # and then, start pulling for new messages
            self.updater.start_polling(drop_pending_updates=True)
            while not self.updater.running:
                pass

            # self.port = int(os.environ.get('PORT', '80'))
            # self.updater.start_webhook(listen="0.0.0.0",
            #                            port=self.port,
            #                            url_path=telegram_token,
            #                            webhook_url="https://f6308748adc5.ngrok.io/webhook",
            #                            drop_pending_updates=True,
            #                            )


@w.route('/')
def index():
    return 'Ping page'


class WebRequestResponse(Thread):
    """Run a webpage"""

    def __init__(self):
        self.port = int(os.environ.get('PORT', '8484'))
        Thread.__init__(self, name='Web', args=())
        self.daemon = True
        self.start()

    def run(self):
        w.run(threaded=True, port=self.port)


def telegram_data(update, updater, good_reads):
    """All received Telegram messages is queued here"""
    try:
        query = update.callback_query
        query.answer('Por favor, aguarde!!')
        data_digest(query, updater, good_reads)
    except Exception as e:
        logger.exception('{}'.format(e), exc_info=False)


def telegram_message(update, good_reads):
    """All received Telegram messages is queued here"""
    try:
        message_digest(update, good_reads)
    except Exception as e:
        logger.exception('{}'.format(e), exc_info=False)


def start(update):
    """
    Show an welcome message.
    """
    send_picture(update, open('Pictures/welcome_pic.jpg', 'rb'))

    msg = 'Olá, amigo leitor!\n' \
          'Clique em <i><b>"Adicionar um novo livro"</b></i> para que possamos começar!\n'

    # Start the main menu
    add_keyboard(update, msg, MAIN_MENU_KEYBOARD)


def error(update, context):
    """Log Errors caused by Updates"""
    logger.error('Update "%s" caused error "%s"', update, context.error)


def application(environment):
    """All application has its initialization from here"""
    logger.info('Main application is running!')
    # Count available CPU Cores
    logger.debug("Number of cpu: %s", cpu())

    logger.info('Environment: {}'.format(environment))
    settings = FunctionalSystemSettings(environment)

    good_reads = GoodReadsClient()

    # Initialize Webpage
    # WebRequestResponse()

    # Initializing Telegram
    _telegram = InitializeTelegram(settings, good_reads)

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    _telegram.updater.idle()
    logger.info('Finishing the application')
