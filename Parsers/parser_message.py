# Build-in modules
import logging

# Added modules
# import matplotlib
# import matplotlib.pyplot as plt
# from matplotlib.dates import DateFormatter

# Project modules
# from Database.file import get_directory_path
# from Machine_learning.turing import finish_prediction_polynomial, week_days_reading, clustering, global_mean
# from menus import add_keyboard, MAIN_MENU_KEYBOARD, YOUR_INFO_KEYBOARDS
# from messages import send_message, send_picture

# matplotlib.use('Agg')

logger = logging.getLogger(__name__)


def messages_parser(update, database):
    """
    Incoming message parser
    """

#     # Commands
#     menu_start = ['/start']
#
#     # Main menu
#     menu_status = ['status']
#     menu_community = ['community']
#     menu_your_info = ['general information']
#     menu_recommendation = ['recommendation']
#     menu_help = ['help']
#
#     # Your info menu
#     menu_global = ['reading over time']
#     menu_book = ['current reading']
#     menu_quit = ['leave current reading']
#
#     # Return to main menu
#     menu_return = ['initial menu']
#
#     msg = str(update.message.text)
#     # Check if all book information were filled
#     ret = verify_inconsistent_information(database)
#     if ret is True:
#         msg = msg.lower()
#         # Update database reading numbers
#         update_database_reading_information(database)
#         # --------------------------------------------------------------------------------------------------------------
#         if msg in menu_help:
#             msg = ['<i><b>- Only 1 book can be added at a time.</b></i>',
#                    "<i><b>- To add a new book, just use the Telegram's camera tool to send a photo of the book's "
#                    "barcode you are about to start!</b></i>",
#                    '<i><b>- At the end of your daily reading routine just enter the page number you stopped at and '
#                    'I will make the math for you!</b></i>',
#                    "<i><b>- When the page entered is the last page to be read in the current book, Livoreto will warn "
#                    "you about the book's completion</b></i>",
#                    '<i><b>- Any suggestions, please, send to andre.ribeiro.srs@gmail.com</b></i>']
#             send_message('\n\n'.join(msg), update)
#         # --------------------------------------------------------------------------------------------------------------
#         elif msg in menu_quit:
#             check_book_finish(database, None, update, database, True)
#         # --------------------------------------------------------------------------------------------------------------
#         elif msg in menu_your_info:
#             # Start a new keyboard layout
#             add_keyboard(update, '<i><b>Take a look at your numbers!</b></i>', YOUR_INFO_KEYBOARDS)
#         # --------------------------------------------------------------------------------------------------------------
#         elif msg in menu_recommendation:
#             # Load books from book shelf
#             df_a = database.get_value('tHISTORY')
#             df_b = database.get_value('tREADING')
#
#             if (df_a is not None) or (df_b is not None):
#                 # Start the book recommendation process
#                 pending_jobs['recommendation'] = str(update.message.chat_id)
#                 send_message(
#                     'This will take some time! As soon as the result is ready, I will send a message to you with '
#                     'the recommendations!', update)
#             else:
#                 send_message("You did not read books yet! You need to read some first and then I will recommend others "
#                              "for you!", update)
#         # --------------------------------------------------------------------------------------------------------------
#         elif msg in menu_start:
#             """
#             Show an welcome message.
#             """
#             send_picture(update, open('Pictures/welcome_pic.jpg', 'rb'))
#
#             msg = "Very welcome, dear reader!\n" \
#                   "To begin, I need the barcode (ISBN code) picture from the book you are going to read.\n" \
#                   'Enter with "Help" to read about more usage details'
#
#             # Start the main menu
#             add_keyboard(update, msg, MAIN_MENU_KEYBOARD)
#         # --------------------------------------------------------------------------------------------------------------
#         elif msg in menu_status:
#             df = database.get_value('tREADING')
#
#             if df is not None:
#                 book_status(update, database)
#             else:
#                 add_keyboard(update, "There is no reading in progress!", MAIN_MENU_KEYBOARD)
#         # --------------------------------------------------------------------------------------------------------------
#         elif msg in menu_global:
#
#             books_name, qty = get_current_year_book_list(database)
#
#             send_message('Qty. of books read so far: <i><b>{}</b></i>\n'.format(qty), update)
#
#             if qty > 0:
#                 send_message('They are ...\n\n'
#                              '<i><b>{}</b></i>'.format(books_name), update)
#
#             pages = all_pages_read(database)
#             if pages > 0:
#                 send_message('Total of pages read: <i><b>{}</b></i>!\n'.format(pages), update)
#
#             mean = round(global_mean(database), 0)
#             if mean > 0:
#                 send_message('Average pages read a day is <i><b>{}</b></i>!\n'.format(mean), update)
#
#             max_days = max_days_streak(database)
#             if max_days > 0:
#                 send_message('Max. number of days reading in sequence is <i><b>{}</b></i>!\n'.format(max_days), update)
#
#             chat_id = str(update.message.chat_id)
#             max_value, min_value = week_days_reading(database, chat_id)
#             if max_value is not False:
#                 send_message('<i><b>{}</b></i> is the day of the week that you read the most!\n'.format(max_value),
#                              update)
#                 send_message('<i><b>{}</b></i> is the day of the week that you least read!\n'.format(min_value), update)
#
#                 send_picture(update, open('Database/pie_{}.png'.format(chat_id), 'rb'))
#
#                 path = get_directory_path()
#                 if os.path.exists("{}/{}".format(path, 'pie_{}.png'.format(chat_id))):
#                     # Delete the sent picture.
#                     os.remove("{}/{}".format(path, 'pie_{}.png'.format(chat_id)))
#
#             clusters = clustering(database)
#             if clusters is not False:
#                 when = ['<i><b>{:0>2}:{:0>2}</b></i>'.format(values.hour, values.minute) for values in clusters]
#                 when = '\n'.join(when)
#                 send_message('You usually read around ...\n{}'.format(when), update)
#
#             if mean > 0:
#                 df = database.get_value('tPAGES')
#                 if df is not None:
#                     pages = df['QUANTITY'].tail(n=15).tolist()
#                     timestamp = df['TIMESTAMP'].tail(n=15).tolist()
#
#                     if len(timestamp) > 7:
#                         plt.clf()
#                         date = []
#                         for values in timestamp:
#                             day = datetime.fromtimestamp(values)
#                             new_day = day.replace(hour=0, minute=0, second=0)
#                             date.append(new_day)
#
#                         ax = plt.gca()
#                         ax.xaxis.set_major_formatter(DateFormatter('%d-%b'))
#                         plt.bar(date, pages, color='blue', width=0.5)
#                         if mean > 0:
#                             plt.axhline(y=mean, color='r', linestyle='--')
#                         plt.xticks(rotation=25)
#                         plt.title('Last 15 days in numbers')
#                         plt.ylabel('Pages qty.')
#                         plt.grid()
#                         plt.savefig('./Database/last_pages_qty_{}.png'.format(chat_id))
#                         send_picture(update, open('Database/last_pages_qty_{}.png'.format(chat_id), 'rb'))
#
#                         path = get_directory_path()
#                         if os.path.exists("{}/{}".format(path, 'last_pages_qty_{}.png'.format(chat_id))):
#                             # Delete the sent picture.
#                             os.remove("{}/{}".format(path, 'last_pages_qty_{}.png'.format(chat_id)))
#
#             df = database.get_value('tREADING')
#             if df is None:
#                 send_message('You are not reading a book at this moment!\n\n', update)
#         # --------------------------------------------------------------------------------------------------------------
#         elif msg in menu_book:
#
#             df = database.get_value('tREADING')
#
#             if df is None:
#                 send_message('You are not reading a book at this moment!\n\n', update)
#             else:
#                 isbn_value = df['ISBN'][df.index[0]]
#                 book_info = isbn_lookup(isbn_value)
#
#                 # Check for a valid information
#                 if len(book_info) > 0:
#                     msg = ['<i><b>{}</b></i>: {}\n'.format(value, key) for value, key in book_info.items()]
#                     send_message(''.join(msg), update)
#
#                     total = df['END_PAGE'][df.index[0]] - df['START_PAGE'][df.index[0]]
#                     send_message('Total pages: <i><b>{}</b></i>\n'.format(total), update)
#                 else:
#                     send_message('Something went wrong. Please, try again.', update)
#         # --------------------------------------------------------------------------------------------------------------
#         elif msg in menu_return:
#             # Return to main keyboard
#             msg = '<i><b>Check your current reading and others!</b></i>'
#             add_keyboard(update, msg, MAIN_MENU_KEYBOARD)
#         # --------------------------------------------------------------------------------------------------------------
#         elif msg in menu_community:
#             reading_books_list = []
#             # Close the current database connection
#             database.disconnect_database(server_close=False)
#             # Fetch database names
#             db_names = database.client.list_databases()
#
#             for names in db_names:
#                 # Exclude default databases
#                 if names != ('admin' and 'config' and 'local'):
#                     # Connecting to database file
#                     database.connect_database(names['name'])
#                     # Refresh database information
#                     database.refresh_database()
#                     # Bring the current reading
#                     df = database.get_value('tREADING')
#                     # Check if it is empty
#                     if df is not None:
#                         reading_books_list.append('- ' + df['BOOK'][df.index[0]])
#
#                 # Close database file
#                 database.disconnect_database(server_close=False)
#
#             msg = '\n'.join(reading_books_list) if len(reading_books_list) > 0 else 'No one in our community has an ' \
#                                                                                     'active reading right now!'
#
#             send_message(msg, update)
#         # --------------------------------------------------------------------------------------------------------------
#         else:
#             if msg.isdigit():
#                 df = database.get_value('tREADING')
#                 if df is not None:
#                     if add_stop_page(database, int(msg), 0):
#                         if check_book_finish(database, int(msg), update, database) is False:
#                             book_status(update, database)
#                 else:
#                     # Update the keyboard format and send the message
#                     add_keyboard(update, 'You are not reading a book at this moment!', MAIN_MENU_KEYBOARD)
#             else:
#                 # Update the keyboard format and send the message
#                 add_keyboard(update, "I didn't understand, please, try again", MAIN_MENU_KEYBOARD)
#         # --------------------------------------------------------------------------------------------------------------
#     else:
#         if ret == 'new_book':
#             df = database.get_value('tREADING')
#             start = df['START_PAGE'][df.index[0]]
#             end = df['END_PAGE'][df.index[0]]
#
#             if msg.isdigit():
#                 if start == 0:
#                     start = int(msg)
#                 else:
#                     end = int(msg)
#                     if start >= end:
#                         send_message("The final page number can't be less than the initial page number.", update)
#                         end = int(0)
#
#                 df.loc[0, 'START_PAGE'] = start
#                 df.loc[0, 'END_PAGE'] = end
#                 database.add_information('tREADING', df)
#
#             if start == 0:
#                 send_message('Please, enter the number of the first page you will read! ', update)
#             elif end == 0:
#                 send_message('Please, enter the number of the last page you will read!', update)
#             else:
#                 start_day = int(time.time())
#                 df.loc[0, 'START_DAY'] = start_day
#                 df.loc[0, 'TIMESTAMP'] = start_day
#                 df.loc[0, 'BOOK_PAGE'] = start
#                 database.add_information('tREADING', df)
#
#                 send_message('Cool, I am now effectively calculating your numbers!', update)
#
#
# def book_status(update, tables):
#     """
#     Report all book status
#     """
#     df = tables.get_value('tPAGES')
#     qty_pages = df['QUANTITY'][df.index[-1]]
#
#     df = tables.get_value('tREADING')
#     book = df['BOOK'][df.index[0]]
#     last_page = df['BOOK_PAGE'][df.index[-1]]
#     end = df['END_PAGE'][df.index[0]]
#     qty_finish = end - last_page
#
#     msg = ['Stopped at: <i><b>{}</b></i>\n\n'.format(last_page),
#            'Reading: <i><b>{}</b></i>\n'.format(book),
#            'Remaining: <i><b>{}</b></i>\n'.format(qty_finish),
#            'Percentage: <i><b>{}%</b></i>\n'.format(percentage_read(tables)),
#            "Today's pages: <i><b>{}</b></i>".format(qty_pages)]
#
#     send_message(''.join(msg), update)
#
#     start_day_epoch = df['START_DAY'][df.index[0]]
#     local_time_adjust = time.localtime(start_day_epoch)
#     started_at = time.strftime('%A, %d %b %Y', local_time_adjust)
#
#     # Update the keyboard format and send the message
#     add_keyboard(update, 'Started at: {}'.format(started_at), MAIN_MENU_KEYBOARD)
#
#     chat_id = str(update.message.chat_id)
#     book = finish_prediction_polynomial(tables, chat_id)
#     if book is not False:
#         send_message('<i><b>Expected to end in: {}</b></i>'.format(book), update)
#         send_picture(update, open('Database/polynomial_regression_{}.png'.format(chat_id), 'rb'))
#
#         path = get_directory_path()
#         if os.path.exists("{}/{}".format(path, 'polynomial_regression_{}.png'.format(chat_id))):
#             # Delete the sent picture.
#             os.remove("{}/{}".format(path, 'polynomial_regression_{}.png'.format(chat_id)))
#
#     qty = days_streak(tables)
#     if qty > 1:
#         send_message('You are <i><b>{} days</b></i> reading in sequence!'.format(qty), update)
#
#
# def add_stop_page(database, page, delta):
#     """
#     Save the last page read
#     """
#     df = database.get_value('tREADING')
#
#     if verify_if_epoch_is_today(df['TIMESTAMP'][df.index[-1]]) == 0:
#         same_day = True
#         last_page = df['START_PAGE'][df.index[0]] if len(df.index) == 1 else df['BOOK_PAGE'][df.index[-2]]
#     else:
#         same_day = False
#         last_page = df['BOOK_PAGE'][df.index[-1]]
#
#     if page >= last_page:
#         total = page - last_page
#         date = (datetime.today() - timedelta(days=delta))
#         timestamp = int(datetime.timestamp(date))
#
#         if same_day:
#             # Calculate the pages qty since last time
#             dif = total - df['PAGE'][df.index[-1]]
#
#             # Update the last page read number
#             index = len(df.index) - 1
#             df.loc[index, 'PAGE'] = total
#             df.loc[index, 'BOOK_PAGE'] = page
#             df.loc[index, 'TIMESTAMP'] = timestamp
#         else:
#             # Calculate the pages qty since last time
#             dif = total
#
#             # Create a new row with the page number of that day
#             df = df.append({'BOOK': None,
#                             'AUTHOR': None,
#                             'PUBLISHER': None,
#                             'PUBLICATION_DATE': None,
#                             'EDITION': None,
#                             'BOOK_COVER': None,
#                             'LANGUAGE': None,
#                             'GENRE': None,
#                             'ISBN': None,
#                             'REMARK': None,
#                             'START_PAGE': None,
#                             'END_PAGE': None,
#                             'START_DAY': None,
#                             'END_DAY': None,
#                             'PAGE': total,
#                             'BOOK_PAGE': page,
#                             'TIMESTAMP': timestamp}, ignore_index=True)
#
#         database.add_information('tREADING', df)
#
#         df = database.get_value('tPAGES')
#         if df is not None:
#             today = datetime.today()
#             date = datetime.fromtimestamp(df['TIMESTAMP'][df.index[-1]])
#
#             if today.date() == date.date():
#                 # Update the total pages read today
#                 index = len(df.index) - 1
#                 df.loc[index, 'QUANTITY'] = df['QUANTITY'][df.index[-1]] + dif
#                 df.loc[index, 'TIMESTAMP'] = timestamp
#             else:
#                 # create a new row with the quantity of that day
#                 df = df.append({'QUANTITY': dif,
#                                 'TIMESTAMP': timestamp}, ignore_index=True)
#         else:
#             # create a new row with the quantity of that day
#             df = {'QUANTITY': dif,
#                   'TIMESTAMP': timestamp}
#
#         database.add_information('tPAGES', df)
#
#         return True
#     else:
#         return False
#
#
# def check_book_finish(database, page, update, tables, quit_book=False):
#     """
#     With the new page input, check if the book was finished
#     """
#     df = tables.get_value('tREADING')
#
#     if quit_book:
#         # check if there is a current book reading
#         if df is not None:
#             database.drop_collection('tREADING')
#             send_message('You have abandoned your current reading!', update)
#         else:
#             add_keyboard(update, 'You are not reading a book at this moment!', MAIN_MENU_KEYBOARD)
#     else:
#         if df['END_PAGE'][df.index[0]] == page:
#             df.loc[0, 'END_DAY'] = int(time.time())
#             new_table = 't{}'.format(int(time.time()))
#             database.add_information(new_table, df)
#
#             total_pages = df['END_PAGE'][df.index[0]] - df['START_PAGE'][df.index[0]]
#
#             start_day = datetime.fromtimestamp(df['START_DAY'][df.index[0]])
#             final_day = datetime.fromtimestamp(df['END_DAY'][df.index[0]])
#             delta = (final_day - start_day).days + 1
#
#             local_time_adjust = time.localtime(df['START_DAY'][df.index[0]])
#             started_at = time.strftime('%A, %d %b %Y', local_time_adjust)
#
#             database.drop_collection('tREADING')
#
#             df = tables.get_value('tHISTORY')
#             if df is not None:
#                 df = df.append({'BOOK_TABLE_NAME': new_table}, ignore_index=True)
#             else:
#                 df = {'BOOK_TABLE_NAME': new_table}
#
#             database.add_information('tHISTORY', df)
#
#             send_message('Excellent!! You just finished one more book!', update)
#             send_message('You read {} pages.\n'
#                          'Along of {} days.\n'
#                          'Started in: {}'.format(total_pages, delta, started_at), update)
#             return True
#         else:
#             return False
#
#
# def percentage_read(tables):
#     """
#     Calculate the percentage read
#     """
#     df = tables.get_value('tREADING')
#
#     end = df['END_PAGE'][df.index[0]]
#     start = df['START_PAGE'][df.index[0]]
#     whole = end - start
#     part = df['BOOK_PAGE'][df.index[-1]] - start
#
#     return format(100 * float(part / whole), '.2f')
#
#
# def verify_if_epoch_is_today(epoch):
#     """
#     Check if Today is the same as a given epoch.
#     If not, return a delta between both
#     """
#     today = datetime.today()
#     then = datetime.fromtimestamp(epoch)
#
#     if today.date() == then.date():
#         return 0
#     else:
#         return abs((today.date() - then.date()).days)
#
#
# def get_current_year_book_list(database):
#     """
#     Get a list of book that were read the current year
#     """
#     df = database.get_value('tHISTORY')
#     qty = 0
#     books_names = ''
#
#     if df is not None:
#         qty = df['BOOK_TABLE_NAME'].count()
#
#         if qty > 0:
#             table_list = df['BOOK_TABLE_NAME'].tolist()
#             books_name = []
#             for name in table_list:
#                 df = database.get_value('{}'.format(name))
#                 books_name.append('- ' + df['BOOK'][df.index[0]])
#             books_names = '\n'.join(books_name)
#
#     return books_names, qty
#
#
# def all_pages_read(tables):
#     """
#     Sun of all pages read
#     """
#     df = tables.get_value('tPAGES')
#     if df is not None:
#         pages = df['QUANTITY'].tolist()
#
#         if len(pages) > 0:
#             return sum(pages)
#
#     return int(0)
#
#
# def days_streak(tables):
#     """
#     Return how many days the user is reading without a break
#     """
#     qty = 0
#     df = tables.get_value('tPAGES')
#     if df is not None:
#         pages = df['QUANTITY'].tolist()
#         pages.reverse()
#         for i in pages:
#             if i != 0:
#                 qty += 1
#             else:
#                 break
#     return qty
#
#
# def max_days_streak(tables):
#     """Return the max number of how many days the user read without a break"""
#     qty = 0
#     mx = 0
#     df = tables.get_value('tPAGES')
#     if df is not None:
#         pages = df['QUANTITY'].tolist()
#         for i in pages:
#             if i != 0:
#                 qty += 1
#                 if qty > mx:
#                     mx = qty
#             else:
#                 qty = 0
#     return mx
#
#
# def verify_inconsistent_information(database):
#     """Check if the current database has some missing information"""
#
#     ret = True
#
#     # Bring the current reading
#     df = database.get_value('tREADING')
#     # Check if it is empty
#     if df is not None:
#         start = df['START_PAGE'][df.index[0]]
#         end = df['END_PAGE'][df.index[0]]
#         if start == 0 or end == 0:
#             ret = 'new_book'
#
#     return ret
#
#
# def update_database_reading_information(database):
#     """
#     Update all database reading numbers based on Today's date
#     """
#     # check if there is a reading in progress
#     df = database.get_value('tREADING')
#     if df is not None:
#         delta = verify_if_epoch_is_today(df['TIMESTAMP'][df.index[-1]])
#         # Check if there is a delta between the last page read and today
#         if delta > 0:
#             # If yes, the tReading database will be filled up with zeros from the last day until today
#             while delta > 0:
#                 # Fetch the last page read
#                 last_page = df['BOOK_PAGE'][df.index[-1]]
#                 # Update the database
#                 add_stop_page(database, last_page, delta - 1)
#                 logger.info('(tREADING) Adjusting database delta ({})'.format(delta))
#                 # Run 1 day forward
#                 delta -= 1
#                 # Refresh tables information
#                 database.refresh_database()
#     else:
#         # Check if the user finished a book today
#         df = database.get_value('tPAGES')
#         if df is not None:
#             delta = verify_if_epoch_is_today(df['TIMESTAMP'][df.index[-1]])
#             if delta > 0:
#                 while delta > 0:
#                     date = (datetime.today() - timedelta(days=delta - 1))
#                     timestamp = int(datetime.timestamp(date))
#                     df = df.append({'QUANTITY': int(0), 'TIMESTAMP': timestamp}, ignore_index=True)
#                     logger.info('(tPAGES) Adjusting database delta ({})'.format(delta))
#                     # Run 1 day forward
#                     delta -= 1
#
#                 database.add_information('tPAGES', df)
#
#                 # Refresh tables information
#                 database.refresh_database()
