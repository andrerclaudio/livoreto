# Build-in modules
import configparser
import logging
import os
import time
from multiprocessing import Process, cpu_count as cpu
from multiprocessing import ProcessError
from threading import Thread

# Added modules
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler, CommandHandler

# Project modules
from Machine_learning.recommender_system import recommendation_tree
from delivery import send_picture
from menus import add_keyboard, MAIN_MENU_KEYBOARD
from settings import settings
from system_digest import message_digest, data_digest

if settings.WORK_MODE == 'prod&pc':
    # Print in file
    logging.basicConfig(filename='logs.log',
                        filemode='w',
                        level=logging.INFO,
                        format='%(asctime)s | %(process)d | %(name)s | %(thread)d | %(threadName)s | %(levelname)s: '
                               '%(message)s',
                        datefmt='%d/%b/%Y - %H:%M:%S')
else:
    # Print in software terminal
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s | %(process)d | %(threadName)s | %(levelname)s: '
                               '%(message)s',
                        datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)


class InitializeTelegram(object):
    """Telegram Bot initializer"""

    def __init__(self):
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
        data_handler = CallbackQueryHandler(lambda update, context: telegram_data(update, self.updater))
        msg_handler = MessageHandler(Filters.text, lambda update, context: telegram_message(update))

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


class ProcessRecommendationSystem(Thread):
    """Process the recommendation system"""

    def __init__(self):
        Thread.__init__(self, name='Recommendation system', args=())
        self.daemon = True
        self.start()

    def run(self):
        logger.info('[START] Recommendation system!')
        while True:
            """Periodically calls for recommendation machine"""
            if (time.time() - settings.last_recommendation_run >= settings.DELTA and settings.running_recommender) or \
                    settings.run_at_initialization:

                settings.run_at_initialization = False
                try:
                    settings.running_recommender = False
                    p = Process(target=recommendation_tree,
                                name='Recommender system')
                    p.daemon = True
                    p.start()
                    p.join()
                except ProcessError as e:
                    logger.exception('{}'.format(e), exc_info=False)
                finally:
                    # Signalize a new running can happen
                    settings.running_recommender = True
                    # Register when the task have finished
                    settings.last_recommendation_run = time.time()


def telegram_data(update, updater):
    """All received Telegram messages is queued here"""
    try:
        query = update.callback_query
        query.answer('Por favor, aguarde!!')
        data_digest(query, updater)
    except Exception as e:
        logger.exception('{}'.format(e), exc_info=False)


def telegram_message(update):
    """All received Telegram messages is queued here"""
    try:
        message_digest(update)
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


def application():
    """All application has its initialization from here"""
    logger.info('Main application is running!')
    # Count available CPU Cores
    logger.debug("Number of cpu: %s", cpu())

    # Initializing Telegram
    _telegram = InitializeTelegram()

    # Start processing recommendation system
    # ProcessRecommendationSystem()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    _telegram.updater.idle()
    logger.info('Finishing the application')
