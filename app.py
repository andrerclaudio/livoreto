# Build-in modules
import configparser
import logging
from multiprocessing import cpu_count as cpu
from queue import Queue
from threading import Thread

# Added modules
from telegram.ext import Updater, MessageHandler, Filters

# Project modules

""" ----  Mode work options ------
Development    = 'dev'
Production     = 'prod'
------------------------------ """
WORK_MODE = 'dev'

if WORK_MODE == 'prod':
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
                        format='%(asctime)s | %(process)d | %(name)s | %(thread)d | %(threadName)s | %(levelname)s: '
                               '%(message)s',
                        datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)


class InitializeTelegram(object):
    """Telegram Bot initializer"""

    def __init__(self):
        # Configuring bot
        config = configparser.ConfigParser()
        config.read_file(open('config.ini'))
        if WORK_MODE == 'dev':
            telegram_token = config['DEV']['token']
        else:
            # 'prod'
            telegram_token = config['DEFAULT']['token']

        # Telegram incoming messages Queue initializer
        self.msg_queue = Queue()

        # Connecting to Telegram API
        self.updater = Updater(token=telegram_token, use_context=True)
        dispatcher = self.updater.dispatcher

        # Creating handlers
        msg_handler = MessageHandler(Filters.text, lambda update, context: telegram_message(update, self.msg_queue))

        # Message handler must be the last one
        dispatcher.add_handler(msg_handler)

        # log all errors
        dispatcher.add_error_handler(error)

        # and then, start pulling for new messages
        self.updater.start_polling(drop_pending_updates=True)

        while not self.updater.running:
            pass


class ProcessIncomingMessages(Thread):
    """Start processing all Telegram incoming messages"""

    def __init__(self, telegram_obj):
        self.msg_queue = telegram_obj.msg_queue
        Thread.__init__(self, name='Message dispatcher', args=())
        self.daemon = True
        self.start()

    def run(self):
        """Process messages"""
        while True:
            self.msg_queue.get()
            logger.info('[Message queue: {}]'.format(self.msg_queue.qsize()))


def application():
    """All application has its initialization from here"""
    logger.info('Main application is running!')
    # Count available CPU Cores
    logger.debug("Number of cpu: %s", cpu())

    # Initializing Telegram
    _telegram = InitializeTelegram()

    # Start processing all Telegram messages
    ProcessIncomingMessages(_telegram)


def telegram_message(update, msg_queue):
    """All received Telegram messages is queued here"""
    try:
        logger.debug('{}'.format(update.message.chat_id))

        # Message Queue
        msg_queue.put(update)
        logger.info('[Message queue: {}]'.format(int(msg_queue.qsize())))
    except Exception as e:
        logger.exception('{}'.format(e), exc_info=False)


def error(update, context):
    """Log Errors caused by Updates"""
    logger.error('Update "%s" caused error "%s"', update, context.error)