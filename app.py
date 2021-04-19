# Build-in modules
import configparser
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

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    return 'Ping page'


class WebRequestResponse(Thread):
    """Run a webpage"""

    def __init__(self):
        self.port = 80
        Thread.__init__(self, name='Web', args=())
        self.daemon = True
        self.start()

    def run(self):
        app.run(threaded=True, port=self.port)


class FunctionalSystemSettings(object):

    def __init__(self, environment):
        # --------------------------------------------------------------------------------
        """ ----------- Mode work options -----------
        Development and Notebook  = 'dev&pc'
        Production and Cloud      = 'prod&cloud'
        ----------------------------------------- """
        if environment == 'Heroku':
            self.WORK_MODE = 'prod&cloud'
        else:
            self.WORK_MODE = 'dev&pc'
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
        if settings.WORK_MODE == 'dev&cloud':
            telegram_token = os.environ['DEV']
        elif settings.WORK_MODE == 'prod&cloud':
            telegram_token = os.environ['DEFAULT']
        else:
            config = configparser.ConfigParser()
            config.read_file(open('config.ini'))
            if settings.WORK_MODE == 'dev&pc':
                telegram_token = config['DEV']['token']
            else:
                # 'prod&pc'
                telegram_token = config['DEFAULT']['token']

        # Connecting to Telegram API
        self.updater = Updater(token=telegram_token, use_context=True)
        dispatcher = self.updater.dispatcher

        # Creating handlers
        start_handler = CommandHandler('start', lambda update, context: start(update))
        data_handler = CallbackQueryHandler(
            lambda update, context: telegram_data(update, self.updater, settings, good_reads))
        msg_handler = MessageHandler(Filters.text,
                                     lambda update, context: telegram_message(update, settings, good_reads))

        # Message handler must be the last one
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(data_handler)
        dispatcher.add_handler(msg_handler)

        # log all errors
        dispatcher.add_error_handler(error)

        if settings.WORK_MODE == 'dev&cloud' or settings.WORK_MODE == 'prod&cloud':
            self.port = int(os.environ.get('PORT', '80'))
            self.updater.start_webhook(listen="0.0.0.0",
                                       port=self.port,
                                       url_path=telegram_token,
                                       webhook_url="https://livoreto.herokuapp.com/{}".format(telegram_token)
                                       )
            # self.updater.idle()
        else:
            # and then, start pulling for new messages
            self.updater.start_polling(drop_pending_updates=True)
            while not self.updater.running:
                pass


# class ProcessRecommendationSystem(Thread):
#     """Process the recommendation system"""
#
#     def __init__(self, settings):
#         self.settings = settings
#         Thread.__init__(self, name='Recommendation system', args=())
#         self.daemon = True
#         self.start()
#
#     def run(self):
#         logger.info('[START] Recommendation system!')
#         while True:
#             """Periodically calls for recommendation machine"""
#             if (time.time() - self.settings.last_recommendation_run >= self.settings.DELTA and self.settings.running_recommender) or self.settings.run_at_initialization:
#
#                 self.settings.run_at_initialization = False
#                 try:
#                     self.settings.running_recommender = False
#                     p = Process(target=recommendation_tree,
#                                 name='Recommender system')
#                     p.daemon = True
#                     p.start()
#                     p.join()
#                 except ProcessError as e:
#                     logger.exception('{}'.format(e), exc_info=False)
#                 finally:
#                     # Signalize a new running can happen
#                     self.settings.running_recommender = True
#                     # Register when the task have finished
#                     self.settings.last_recommendation_run = time.time()


def telegram_data(update, updater, settings, good_reads):
    """All received Telegram messages is queued here"""
    try:
        query = update.callback_query
        query.answer('Por favor, aguarde!!')
        data_digest(query, updater, settings, good_reads)
    except Exception as e:
        logger.exception('{}'.format(e), exc_info=False)


def telegram_message(update, settings, good_reads):
    """All received Telegram messages is queued here"""
    try:
        message_digest(update, settings, good_reads)
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

    good_reads = GoodReadsClient(settings)

    # Initializing Telegram
    # _telegram = InitializeTelegram(settings, good_reads)

    # Start processing recommendation system
    # ProcessRecommendationSystem(settings)

    # Initialize Webpage
    WebRequestResponse()

    while True:
        pass

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    # _telegram.updater.idle()
    # logger.info('Finishing the application')
