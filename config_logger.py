import logging, os

def do_config():

    logger = logging.getLogger('de.mineway.msworkbench')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    op = os.path
    try:
        os.mkdir("logs")
    except:
        pass

    fh = logging.FileHandler('logs/msworkbench.log')
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARN)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(process)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    __builtins__["LLL"] = logger

