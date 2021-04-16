import sys

# Import the main application
from app import application


def main():
    application(environment)
    return None


if __name__ == "__main__":
    # Parse if it is started from Cloud or not
    if len(sys.argv) > 1:
        environment = sys.argv[1]
    else:
        environment = 'Local'

    # Run the main function.
    main()
