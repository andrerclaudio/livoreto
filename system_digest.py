# Build-in modules
import logging
import time
from datetime import timedelta, datetime, timezone

# Added modules
from pytictoc import TicToc

# Project modules
from Database.database import DatabaseCollections, MongoDBConnection
from Parsers.parser_data import data_callback_parser
from Parsers.parser_message import messages_parser

logger = logging.getLogger(__name__)


class ElapsedTime(object):
    """Measure the elapsed time between Tic and Toc"""

    def __init__(self):
        self.t = TicToc()
        self.t.tic()

    def elapsed(self):
        _elapsed = self.t.tocvalue()
        d = timedelta(seconds=_elapsed)
        logger.debug('< {} >'.format(d))


def data_digest(update, telegram_obj):
    """Process data callback information"""
    # Connect to Mongo DB Database
    mongo = MongoDBConnection()
    # Check if the connection is fine
    if mongo.create_connection():
        # Hold tables information
        db = DatabaseCollections(mongo.client)
        # Calculate the elapsed time to process the incoming information
        elapsed = ElapsedTime()
        # Process incoming messages
        try:
            query = update.callback_query
            chat_id = str(query.from_user['id'])
            # Connect to Database
            db.connect(chat_id)
            # Fetch collections data
            db.refresh()
            # Call the data callback parser
            data_callback_parser(update, telegram_obj, db)
            # And then, close the database
            db.disconnect()

            elapsed.elapsed()
        except Exception as e:
            logger.exception('{}'.format(e), exc_info=False)


def message_digest(update):
    """Process message information"""
    # Connect to Mongo DB Database
    mongo = MongoDBConnection()
    # Check if the connection is fine
    if mongo.create_connection():
        # Hold tables information
        db = DatabaseCollections(mongo.client)
        # Calculate the elapsed time to process the incoming information
        elapsed = ElapsedTime()
        # Process incoming messages
        try:
            # Parse the incoming user credentials and open its database file
            verify_user_credentials(update, db)
            # Call the message parser
            messages_parser(update, db)
            # And then, close the database
            db.disconnect()

            elapsed.elapsed()
        except Exception as e:
            logger.exception('{}'.format(e), exc_info=False)


def verify_user_credentials(update, database):
    """Register the incoming user credentials"""

    chat_id = str(update.message.chat_id)

    # Connect to Database
    database.connect(chat_id)
    # Fetch collections data
    database.refresh()

    # Register user access
    user = register_user_access(update, database)
    logger.info('Registered access to: {}'.format(user))


def register_user_access(update, database):
    """Incoming data are registered and labeled to an user.
    For a know user, the access count is increased, otherwise, a new database file will
    be generate"""
    df = database.get('tUSER')

    last_access = int(time.time())
    tzinfo = str(datetime.now(timezone.utc).astimezone().tzinfo)

    if df is not None:
        df = df[0]
        # Update the user information
        obj_id = df['_id']
        counter = df['ACCESS_COUNTER']
        df = {'_id': obj_id,
              'CHAT_ID': df['CHAT_ID'],
              'NAME': df['NAME'],
              'USERNAME': df['USERNAME'],
              'LAST_ACCESS': last_access,
              'TZINFO': tzinfo,
              'ACCESS_COUNTER': int(counter + 1)
              }
        database.update_document('tUSER', df)
        name = df['NAME']
    else:
        name = update.effective_user.full_name
        df = {'CHAT_ID': update.message.chat_id,
              'NAME': name,
              'USERNAME': update.effective_user.username,
              'LAST_ACCESS': last_access,
              'TZINFO': tzinfo,
              'ACCESS_COUNTER': int(1)
              }
        database.save_data('tUSER', df)

    return name
