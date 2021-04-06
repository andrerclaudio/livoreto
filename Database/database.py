# Build-in modules
import configparser
import logging
import os

# Added modules
from pymongo import MongoClient

# Project modules
from settings import settings

logger = logging.getLogger(__name__)


class MongoDBConnection(object):
    """
    Create a connection with MongoDB database
    """

    def __init__(self):
        # Connection indexes to database file
        self.client = None

        if settings.WORK_MODE == 'dev&cloud' or settings.WORK_MODE == 'prod&cloud':
            key = os.environ['MONGODB']
        else:
            config = configparser.ConfigParser()
            config.read_file(open('config.ini'))
            key = config['MONGODB']['url']

        self.connection_url = key

    def create_connection(self):
        """Establish database connection"""
        try:
            self.client = MongoClient(self.connection_url)

            logger.debug('Connected to Remote MongoDB [version: {}]'.format(self.client.server_info()['version']))
        except Exception as e:
            logger.exception(e, exc_info=False)
        finally:
            return self.client


class DatabaseCollections(object):
    """Hold all database information in order to speed up the user queries"""

    def __init__(self, database_client):
        self.db = None
        self.connection_flag = False
        self.db_collections = {}
        self.client = database_client

    def _drop_collection(self, collection_name):
        """
        Drop a specific collection
        """
        try:
            collection = self.db[collection_name]
            collection.drop()
            logger.debug('Dropped collection: {}'.format(collection_name))
        except Exception as e:
            logger.exception(e)

    def connect(self, database_name):
        try:
            self.db = self.client[database_name]
            self.connection_flag = True
        except Exception as e:
            logger.exception(e, exc_info=False)

    def disconnect(self, server_close=True):
        """
        Close database connection
        """
        if self.connection_flag:
            try:
                if server_close:
                    self.client.close()
                    self.connection_flag = False
                self.db = None
                self.db_collections.clear()
                logger.debug('The database connection was finished!')
            except Exception as e:
                logger.exception(e)

    def get(self, key):
        self.refresh()
        return self.db_collections.get(key)

    def refresh(self):
        # Refresh table information
        self.db_collections.clear()

        collections_names = self.db.collection_names(include_system_collections=False)

        for name in collections_names:
            collection = self.db[name]
            cursor = collection.find()
            documents = [docs for docs in cursor]
            self.db_collections['{}'.format(name)] = documents

    def save_data(self, collection_name, data):
        """
        Save data to a given Collection
        """
        # Check if there is a valid information to store
        if len(data) > 0:
            try:
                values = self.db[collection_name]  # Create Collection Name
                values.insert_one(data)
                logger.debug('Created collection: {}'.format(collection_name))
            except Exception as e:
                logger.exception(e)

    def update_document(self, collection_name, data):
        """
        Drop a given collection and create it again with new values
        """
        # Check if there is a valid information to store
        if len(data) > 0:
            col = self.db[collection_name]
            col.save(data)
