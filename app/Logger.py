import logging

PRINT_CONSOLE = False


class Logger:
    def __init__(self, log_file='app.log'):
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
        logging.debug(message)
        if PRINT_CONSOLE:
            print(message)

    @staticmethod
    def info(message):
        logging.info(message)
        if PRINT_CONSOLE:
            print(message)

    @staticmethod
    def warning(message):
        logging.warning(message)
        if PRINT_CONSOLE:
            print(message)

    @staticmethod
    def error(message):
        logging.error(message)
        if PRINT_CONSOLE:
            print(message)

    @staticmethod
    def critical(message):
        logging.critical(message)
        if PRINT_CONSOLE:
            print(message)
