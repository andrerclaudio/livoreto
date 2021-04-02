# Build-in modules
import configparser
import logging
import os

# Added modules
from pymongo import MongoClient

# Project modules
from Book.client import WORK_MODE

logger = logging.getLogger(__name__)


class MongoDBConnection(object):
    """
    Create a connection with MongoDB database
    """

    def __init__(self):
        # Connection indexes to database file
        self.client = None
        # self.host_ip = 'localhost'
        # self.host_port = 27017

        if WORK_MODE == 'dev&cloud' or WORK_MODE == 'prod&cloud':
            key = os.environ['MONGODB']
        else:
            config = configparser.ConfigParser()
            config.read_file(open('config.ini'))
            key = config['MONGODB']['url']

        logger.debug('Established database keys!')
        self.connection_url = key

    def create_connection(self):
        """Establish database connection"""
        try:
            # self.client = MongoClient(self.host_ip, self.host_port, connect=False)
            logger.debug('Connecting to MongoDB server...')
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

    def _create_collection(self, collection_name, data):
        """
        Create a new Collection
        """
        try:
            values = self.db[collection_name]  # Create Collection Name
            values.insert_one(data)
            logger.debug('Created collection: {}'.format(collection_name))
        except Exception as e:
            logger.exception(e)

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
                self.db = None
                self.connection_flag = False
                self.db_collections.clear()
                logger.debug('The database connection was finished!')
            except Exception as e:
                logger.exception(e)

    def get(self, key):
        return self.db_collections.get(key)

    def refresh(self):
        # Refresh table information
        self.db_collections.clear()

        collections_names = self.db.collection_names(include_system_collections=False)

        for name in collections_names:
            collection = self.db[name]
            cursor = collection.find_one()
            self.db_collections['{}'.format(name)] = cursor

    def new_collection(self, collection_name, data):
        """
        Create a new collection
        """
        # Check if there is a valid information to store
        if len(data) > 0:
            self._create_collection(collection_name, data)

    def update_value(self, collection_name, data):
        """
        Drop a given collection and create it again with new values
        """
        # Check if there is a valid information to store
        if len(data) > 0:
            self._drop_collection(collection_name)
            self._create_collection(collection_name, data)
