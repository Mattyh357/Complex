import logging

PRINT_CONSOLE = False

class Logger:
    def __init__(self, log_file='app.log'):
        """
        Wrapped for python logging module that saved the messages into the file as well
        and prints them in to the console.
        :param log_file: File where all messages will be recorded.
        """
        logging.basicConfig(
            level=logging.INFO
            , format='%(asctime)s - %(levelname)s - %(message)s'
            , handlers=[
                        logging.FileHandler(log_file)
                        , logging.StreamHandler()
                    ]
        )

    @staticmethod
    def debug(message):
        """
        Logs DEBUG message.
        :param message: Text of the message
        """
        logging.debug(message)
        if PRINT_CONSOLE:
            print(message)

    @staticmethod
    def info(message):
        """
        Logs IFNO message.
        :param message: Text of the message
        """
        logging.info(message)
        if PRINT_CONSOLE:
            print(message)

    @staticmethod
    def warning(message):
        """
        Logs WARNING message.
        :param message: Text of the message
        """
        logging.warning(message)
        if PRINT_CONSOLE:
            print(message)

    @staticmethod
    def error(message):
        """
        Logs ERROR message.
        :param message: Text of the message
        """
        logging.error(message)
        if PRINT_CONSOLE:
            print(message)

    @staticmethod
    def critical(message):
        """
        Logs CRITICAL message.
        :param message: Text of the message
        """
        logging.critical(message)
        if PRINT_CONSOLE:
            print(message)
