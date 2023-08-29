import logging


def setup_logger(name, log_file, level=logging.INFO):
    """Function to set up as many loggers as you want"""

    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z')

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    # If you also want to see logs in the console, add a StreamHandler:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
