# Build-in modules
import logging
import time
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


def message_digest(update, pending_jobs):
    """Process message information"""
    # Connect to Mongo DB Database
    database_client = MongoDBConnection()
    # Check if the connection is fine
    if database_client.create_connection():
        # Hold tables information
        database = DatabaseCollections(database_client.client)
        # Calculate the elapsed time to process the incoming information
        elapsed = ElapsedTime()
        # Process incoming messages
        try:
            # Parse the incoming user credentials and open its database file
            verify_user_credentials(update, database)
            # Call the message parser
            incoming_msg_parser(update, database, pending_jobs)
            # And then, close the database
            database.disconnect_database()

            elapsed.elapsed()
        except Exception as e:
            logger.exception('{}'.format(e), exc_info=False)


def register_user_access(update, database):
    """Incoming data are registered and labeled to an user.
    For a know user, the access count is increased, otherwise, a new database file will
    be generate"""
    df = database.get_value('tUSER')

    name = update.effective_user.full_name
    last_access = int(time.time())

    if df is not None:
        # Update the user information
        counter = df['ACCESS_COUNTER'][df.index[0]]
        df.loc[0, 'LAST_ACCESS'] = last_access
        df.loc[0, 'ACCESS_COUNTER'] = counter + 1
    else:
        df = {'CHAT_ID': update.message.chat_id,
              'NAME': name,
              'USERNAME': update.effective_user.username,
              'LAST_ACCESS': last_access,
              'ACCESS_COUNTER': int(1)
              }

    database.add_information('tUSER', df)

    return name


def verify_user_credentials(update, database, scheduled=False):
    """Register the incoming user credentials"""
    if scheduled:
        chat_id = update
    else:
        chat_id = str(update.message.chat_id)

    # Connect to Database
    database.connect_database(chat_id)
    # Fetch tables information
    database.refresh_database()

    if not scheduled:
        # Register user access
        user = register_user_access(update, database)
        logger.info('Registered access to: {}'.format(user))
