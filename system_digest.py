# Build-in modules
import logging
from datetime import timedelta

# Added modules
from pytictoc import TicToc

# Project modules
from Database.database import DatabaseCollections, MongoDBConnection

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
            # incoming_msg_parser(update, database, pending_jobs)
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

    name = update.effective_user.full_name
    last_access = update.message.date

    if df is not None:
        # Update the user information
        counter = df['ACCESS_COUNTER']
        df = {'CHAT_ID': df['CHAT_ID'],
              'NAME': df['NAME'],
              'USERNAME': df['USERNAME'],
              'LAST_ACCESS': last_access,
              'ACCESS_COUNTER': int(counter + 1)
              }
        database.update_value('tUSER', df)
    else:
        df = {'CHAT_ID': update.message.chat_id,
              'NAME': name,
              'USERNAME': update.effective_user.username,
              'LAST_ACCESS': last_access,
              'ACCESS_COUNTER': int(1)
              }
        database.new_collection('tUSER', df)

    return name
