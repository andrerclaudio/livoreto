# Build-in modules
import os
import sys


def get_directory_path():
    """
    Return the ./Database folder path
    """
    # Store current working directory
    path = os.path.dirname(__file__)

    # Append current directory to the python path
    sys.path.append(path)
    return path
