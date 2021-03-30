# Build-in modules
import logging

# Added modules
import pandas as pd
from bson.objectid import ObjectId
from pymongo import MongoClient

logger = logging.getLogger(__name__)


class MongoDBConnection(object):
    """
    Create a connection with MongoDB database
    """

    def __init__(self):
        # Connection indexes to database file
        self.client = None

    def create_connection(self):
        host_ip = 'localhost'
        host_port = 27017

        try:
            self.client = MongoClient(host_ip, host_port, connect=False)

            logger.debug('Connected to MongoDB [version: {}] IP: {} port: {}'
                         .format(self.client.server_info()['version'], host_ip, host_port))
        except Exception as e:
            logger.exception(e, exc_info=False)
        finally:
            return self.client


class DatabaseCollections(object):
    """Hold all database information in order to speed up .db access"""

    def __init__(self, database_client):
        self.db = None
        self.flag = False
        self.collections = {}
        self.client = database_client

    def _clear_collections(self):
        self.collections.clear()

    def _add_value(self, key, value):
        self.collections['{}'.format(key)] = value

    def get_value(self, key):
        return self.collections.get(key)

    def connect_database(self, database_name):
        try:
            self.db = self.client[database_name]
            self.flag = True
        except Exception as e:
            logger.exception(e, exc_info=False)

    def disconnect_database(self, server_close=True):
        """
        Close the database connection
        """
        if self.flag:
            try:
                if server_close:
                    self.client.close()
                self.db = None
                self.flag = False
                self._clear_collections()
                logger.debug('The database connection was finished!')
            except Exception as e:
                logger.exception(e)

    def refresh_database(self):
        # Refresh table information
        self._clear_collections()

        collections_names = self.db.collection_names(include_system_collections=False)

        for names in collections_names:
            collection = self.db[names]
            cursor = collection.find()
            values = list(cursor)
            df = pd.DataFrame(values)
            self._add_value(names, df)

    def drop_collection(self, collection_name):
        """
        Drop a specific collection
        """
        try:
            collection = self.db[collection_name]
            collection.drop()
            logger.info('Dropped collection: {}'.format(collection_name))
        except Exception as e:
            logger.exception(e)

    def add_information(self, collection_name, data):
        """
        Add a new information to a given collection
        """
        # Check if there is a valid information to store
        if len(data) > 0:

            collections_names = self.db.collection_names(include_system_collections=False)

            # Confirm if the Collection name already exist
            if collection_name in collections_names:

                rows = data.to_dict('records')
                document_obj = data['_id'].to_list()

                collection = self.db[collection_name]

                idx = 0
                for doc_id in document_obj:
                    if isinstance(doc_id, ObjectId):
                        query = {"_id": ObjectId("{}".format(str(doc_id)))}
                        collection.replace_one(query, rows[idx])
                        idx += 1
                    else:
                        break

                qty_rows = len(rows)
                while idx < qty_rows:
                    rows[idx].pop('_id')
                    collection.insert_one(rows[idx])
                    idx += 1
            else:
                if isinstance(data, dict):
                    self._create_collection(collection_name, data)
                else:
                    idx = 0
                    rows = data.to_dict('records')
                    self._create_collection(collection_name, rows[idx])
                    if len(rows) > 1:
                        self.add_information(collection_name, data)

    def _create_collection(self, collection_name, data):
        """
        Create a new Collection
        """
        try:
            values = self.db[collection_name]  # Create Collection Name
            values.insert_one(data)
            logger.info('Created collection: {}'.format(collection_name))
        except Exception as e:
            logger.exception(e)
