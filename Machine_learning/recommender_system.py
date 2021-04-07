# Build-in modules
import logging
from queue import Queue
from threading import Thread, ThreadError

# Added modules
import isbnlib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Project modules
from Book.client import good_reads_client as good_reads
from Database.database import DatabaseCollections, MongoDBConnection

logger = logging.getLogger(__name__)

NUMBER_MAX_THREADS = 64

# Create a Dataframe book information
COLUMNS_NAMES = ['GID', 'ISBN', 'TITLE', 'AVERAGE_RATING', 'RATINGS_COUNT', 'AUTHOR', 'PUBLISHER']
INITIAL_POPULAR_SHELF_INDEX = COLUMNS_NAMES.index('PUBLISHER') + 1
QTY_POPULAR_SHELF = 100
OTHERS_COLUMNS = [str(i) for i in range(QTY_POPULAR_SHELF)]
COLUMNS_NAMES.extend(OTHERS_COLUMNS)
QTY_OF_ROWS = len(COLUMNS_NAMES)


def convert_to_numerical(data, column):
    if len(data) > 0:
        x = len(column) + 1
        for element in data:
            if element not in column.keys():
                column[element] = x
                x += 1


class CategoricalToNumericalConverter(object):
    """Create a dictionary with labels and its respective number format"""

    def __init__(self):
        self.title = {}
        self.author = {}
        self.publisher = {}
        self.shelf = {}

    def transpose_data(self, dataframe):
        logger.debug("Categorizing label 'TITLE' to numbers!")
        convert_to_numerical(dataframe['TITLE'].tolist(), self.title)
        df = dataframe.replace({'TITLE': self.title})

        logger.debug("Categorizing label 'AUTHOR' to numbers!")
        convert_to_numerical(df['AUTHOR'].tolist(), self.author)
        df.replace({'AUTHOR': self.author}, inplace=True)

        logger.debug("Categorizing label 'PUBLISHER' to numbers!")
        convert_to_numerical(df['PUBLISHER'].tolist(), self.publisher)
        df.replace({'PUBLISHER': self.publisher}, inplace=True)

        logger.debug("Categorizing label 'other COLUMNS' to numbers!")
        values = []
        col = [i for i in df.columns][INITIAL_POPULAR_SHELF_INDEX:]
        [values.extend(df[i].tolist()) for i in col]

        convert_to_numerical(values, self.shelf)
        for i in col:
            df.replace({i: self.shelf}, inplace=True)

        return df


def recommendation_tree():
    """A book recommendation system based in books you read in the past"""

    # Initialize the categorical-numerical library
    converter = CategoricalToNumericalConverter()

    # Connect to Mongo DB Database
    mongo = MongoDBConnection()
    # Create  mongoDB connection
    mongo.create_connection()
    # Check if the connection is fine
    if mongo.client:

        # Hold tables information
        db = DatabaseCollections(mongo.client)

        for db_name in mongo.client.list_database_names():

            if (db_name != 'admin') and (db_name != 'local'):

                logger.info('DB Id: {}'.format(db_name))

                # Connect to Database
                db.connect(db_name)
                # Fetch collections data
                db.refresh()
                # Fetch of reading books
                df = db.get('tREADING')

                if df is not None:
                    # Books to be parsed
                    isbn_list = [values['ISBN'] for values in df]

                    if len(isbn_list) > 0:

                        # Fetch all related books ISBN codes information
                        information, similarity = set_information(isbn_list)
                        # Add all info into a Pandas Dataframe
                        books_dataframe = create_dataframe(information)

                        # Find the other books from the same authors
                        authors = books_dataframe['AUTHOR'].tolist()
                        others = []
                        for name in authors:
                            ret = good_reads.find_author(name)
                            if ret:
                                for books in ret.books:
                                    if type(books.isbn13) is str:
                                        others.append(books.isbn13)

                        # Add these books to similar
                        similarity.extend(others)

                        # 1° turn of fetching similar books
                        information, similarity = set_information(similarity)
                        # Add all info into a Pandas Dataframe
                        similarity_dataframe = create_dataframe(information)

                        # 2° turn of fetching similar books
                        information, similarity = set_information(similarity)
                        # Add all info into a Pandas Dataframe
                        similarity_dataframe = pd.concat([create_dataframe(information), similarity_dataframe],
                                                         ignore_index=True)

                        # 3° turn of fetching similar books
                        # information, similarity = set_information(similarity)
                        # Add all info into a Pandas Dataframe
                        # similarity_dataframe = pd.concat([create_dataframe(information), similarity_dataframe], ignore_index=True)

                        # 4° turn of fetching similar books
                        # information, similarity = set_information(similarity)
                        # Add all info into a Pandas Dataframe
                        # similarity_dataframe = pd.concat([create_dataframe(information), similarity_dataframe], ignore_index=True)

                        # Remove duplicate values from Pandas Dataframe
                        similarity_dataframe.drop_duplicates(subset='ISBN', keep='first', inplace=True)

                        numerical_books_dataframe = pd.DataFrame()
                        numerical_similarity_dataframe = pd.DataFrame()
                        numerical_books_dataframe = converter.transpose_data(books_dataframe)
                        numerical_similarity_dataframe = converter.transpose_data(similarity_dataframe)

                        # Run prediction
                        y_pred = list(set(run_prediction(numerical_similarity_dataframe, numerical_books_dataframe)))

                        for codes in y_pred:
                            i = numerical_similarity_dataframe[(numerical_similarity_dataframe['ISBN'] == codes)].index
                            numerical_similarity_dataframe.drop(i, inplace=True)

                        # Run prediction
                        y_pred.extend(
                            list(set(run_prediction(numerical_similarity_dataframe, numerical_books_dataframe))))

                        # Show predicted books
                        ret, _ = set_information(y_pred)
                        predicted_books = create_dataframe(ret)

                        print(predicted_books['TITLE'])

                # And then, close only the database
                db.disconnect(server_close=False)

    # Disconnect the client
    mongo.client.close()

    return


def set_information(isbn_list):
    """ """
    new_threads = 0
    count = 0
    information = []
    similar_books = []
    similar_books_isbn_list = []
    running_processes = []

    # Initialize data sharing
    info_queue = Queue()

    logger.info('Starting fetching process ...')

    while len(isbn_list) > 0:
        running_processes.clear()
        while (new_threads <= NUMBER_MAX_THREADS - 1) and (len(isbn_list) > 0):
            isbn_code = isbn_list.pop()
            try:
                t = Thread(target=book_information_lookup, args=[isbn_code, info_queue])

                t.daemon = True  # Daemonize thread
                t.start()  # Start the execution
                running_processes.append(t)
                new_threads += 1
            except ThreadError as e:
                logger.exception('{}'.format(e), exc_info=False)
                isbn_list.append(isbn_code)
        # Wail for all processes to finish
        [t.join() for t in running_processes]
        count += new_threads
        logger.info('Remaining {} ISBN codes to fetch.'.format(len(isbn_list)))
        new_threads = 0

    while not info_queue.empty():
        ret = info_queue.get()
        if ret is not False:
            information.append(ret)

    # It is needed to avoid breaking in case of missing information
    try:
        for items in information:
            if len(items.similar_books) > 0:
                for similar in items.similar_books:
                    similar_books.append(similar)
    except Exception as e:
        logger.exception('{}'.format(e), exc_info=False)

    try:
        for info in similar_books:
            if (info.isbn13 is not None) and (str(info.isbn13).isnumeric()):
                similar_books_isbn_list.append(int(info.isbn13))
            else:
                int(0)
    except Exception as e:
        logger.exception('{}'.format(e), exc_info=False)

    if len(similar_books_isbn_list) > 0:
        similar_books_isbn_list = list(set(similar_books_isbn_list))
        if 0 in similar_books_isbn_list:
            similar_books_isbn_list.remove(0)

    return information, similar_books_isbn_list


def book_information_lookup(isbn, info_queue):
    """Get info about a book"""
    info = False

    isbn = str(isbn)
    if isbnlib.is_isbn13(isbn):
        try:
            info = good_reads.book(isbn=isbn)
            info_queue.put(info)
        except Exception as e:
            logger.exception('{}'.format(e), exc_info=False)


def create_dataframe(information):
    book_info = []
    df = pd.DataFrame(columns=COLUMNS_NAMES)

    for info in information:

        try:
            temp = []
            _isbn = int(info.isbn13) if info.isbn13 is not None else int(0)
            _gid = int(info.gid) if info.gid is not None else int(0)
            _title = str(info.title) if info.title is not None else str('_')
            _average_rating = float(info.average_rating) if info.average_rating is not None else int(0)
            _ratings_count = int(info.ratings_count) if info.ratings_count is not None else int(0)
            _author = str(info.authors[0]) if info.authors[0] is not None else str('_')
            _publisher = str(info.publisher) if info.publisher is not None else str('_')

            temp.extend([_gid, _isbn, _title, _average_rating, _ratings_count, _author, _publisher])

            for j in info.popular_shelves:
                if len(temp) == QTY_OF_ROWS:
                    break
                temp.append(str(j))

            if len(temp) < QTY_OF_ROWS:
                while len(temp) < QTY_OF_ROWS:
                    temp.append(None)

            if len(temp) > 0:
                book_info.append(temp)

        except Exception as e:
            logger.exception('{}'.format(e), exc_info=False)

    # Add all info into a Pandas Dataframe
    for data in book_info:
        df.loc[len(df)] = data

    return df


def run_prediction(train_database, predict_database):
    """ """

    # Adjust the dataframe information
    col_names = COLUMNS_NAMES[INITIAL_POPULAR_SHELF_INDEX:]
    columns = ['AVERAGE_RATING', 'RATINGS_COUNT', 'AUTHOR', 'PUBLISHER']
    columns.extend(col_names)

    x = train_database[columns]
    y = train_database['ISBN']
    y = y.astype('int')

    # Create a Random Forest Classifier
    logger.info('Running Random Forest Classifier!')
    clf = RandomForestClassifier(n_estimators=100)

    # Splitting the dataset into the Training set and Test set
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=0)

    # Train the model
    clf.fit(x, y)
    # y_pred_test = clf.predict(X_test)

    x_predicted = predict_database[columns]
    y_predicted = clf.predict(x_predicted)

    # df_copy = train_database.copy()
    # asd = y_pred.tolist()
    #
    # index = df_copy[(df_copy['ISBN'] != asd[0])].index
    # df_copy.drop(index, inplace=True)

    # Evaluating the Algorithm
    # print('Mean Absolute Error: ', accuracy_score(y_test, y_pred_test))

    return list(set(y_predicted))
