import logging

MINIMUM_LOGGING_LEVEL = logging.INFO

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

# Credit: eos87 from https://stackoverflow.com/a/11233293/3000206
def setup_logger(name, log_file, level=MINIMUM_LOGGING_LEVEL):
    """Allows logging to multiple different files by different loggers."""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger