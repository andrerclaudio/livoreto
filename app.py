# Build-in modules
import configparser
import logging
import os
import signal
from multiprocessing import Process, cpu_count as cpu
from multiprocessing import ProcessError
from queue import Queue
from threading import Thread

# Added modules
from telegram.ext import Updater, MessageHandler, Filters

# Project modules
from Book.client import WORK_MODE
from system_digest import message_digest

if WORK_MODE == 'prod&rasp' or WORK_MODE == 'prod&cloud':
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
        if WORK_MODE == 'dev&cloud':
            telegram_token = os.environ['DEV']
        elif WORK_MODE == 'prod&cloud':
            telegram_token = os.environ['DEFAULT']
        else:
            config = configparser.ConfigParser()
            config.read_file(open('config.ini'))
            if WORK_MODE == 'dev&rasp':
                telegram_token = config['DEV']['token']
            else:
                # 'prod&rasp'
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

        if WORK_MODE == 'dev&cloud' or WORK_MODE == 'prod&cloud':
            self.port = int(os.environ.get('PORT', '8443'))
            self.updater.start_webhook(listen="0.0.0.0", port=self.port, url_path=telegram_token)
            self.updater.bot.setWebhook("https://livoreto.herokuapp.com/" + telegram_token)
            self.updater.idle()
        else:
            # and then, start pulling for new messages
            self.updater.start_polling(drop_pending_updates=True)
            while not self.updater.running:
                pass


class ChatIdQueue(object):
    """Hold all Chat IDs that are being processed"""

    def __init__(self):
        self.chat_id = {}

    def fetch_id(self, chat_id):
        """Return if a Chat ID process is alive, if not, remove the Chat ID from the Dict"""
        if chat_id in self.chat_id.keys():
            p = self.chat_id[chat_id]
            if p.is_alive():
                return True
            else:
                del self.chat_id[chat_id]

        return False

    def add_id(self, chat_id, process):
        """Hold a Chat ID and its Process number"""
        self.chat_id[chat_id] = process


class ProcessIncomingMessages(Thread):
    """Start processing all Telegram incoming messages"""

    def __init__(self, telegram_obj):
        self.telegram_obj = telegram_obj
        self.msg_queue = telegram_obj.msg_queue
        Thread.__init__(self, name='Message dispatcher', args=())
        self.daemon = True
        self.start()

    def run(self):

        # Start ID queue in order to run just one task per Id
        message_library = ChatIdQueue()

        """Process messages while Telegram is running"""
        while self.telegram_obj.updater.running:

            if self.msg_queue.qsize() > 0:
                update = self.msg_queue.get()
                chat_id = update.message.chat_id
                # Check if the Chat ID is already being processed
                if message_library.fetch_id(chat_id):
                    self.msg_queue.put(update)
                else:
                    try:
                        p = Process(target=message_digest,
                                    args=(update,),
                                    name='Message digest')
                        p.daemon = True
                        p.start()
                        message_library.add_id(chat_id, p)
                    except ProcessError as e:
                        logger.exception('{}'.format(e), exc_info=False)
                    finally:
                        # Show the message queue size
                        logger.info('[Message dequeue: {}]'.format(self.msg_queue.qsize()))


def application():
    """All application has its initialization from here"""
    logger.info('Main application is running!')
    # Count available CPU Cores
    logger.debug("Number of cpu: %s", cpu())

    # Initializing Telegram
    _telegram = InitializeTelegram()

    # Start processing all Telegram messages
    ProcessIncomingMessages(_telegram)

    # Interruption handlers
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, _telegram))
    signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, _telegram))


def telegram_message(update, msg_queue):
    """All received Telegram messages is queued here"""
    try:
        logger.debug('{}'.format(update.message.chat_id))

        # Message Queue
        msg_queue.put(update)
        logger.info('[Message enqueue: {}]'.format(int(msg_queue.qsize())))
    except Exception as e:
        logger.exception('{}'.format(e), exc_info=False)


def error(update, context):
    """Log Errors caused by Updates"""
    logger.error('Update "%s" caused error "%s"', update, context.error)


def signal_handler(sig, frame, _telegram):
    logger.info('Finishing the application')
    _telegram.updater.stop()
