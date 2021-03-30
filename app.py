# Build-in modules
import logging
from multiprocessing import cpu_count as cpu

# Added modules

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
                        format='%(asctime)s | %(process)d | %(name)s | %(levelname)s:  %(message)s',
                        datefmt='%d/%b/%Y - %H:%M:%S')
else:
    # Print in software terminal
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s | %(process)d | %(name)s | %(levelname)s:  %(message)s',
                        datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)


def application():
    """" All application has its initialization from here """
    logger.info('Main application is running!')
    # Count available CPU Cores
    logger.debug("Number of cpu: %s", cpu())
