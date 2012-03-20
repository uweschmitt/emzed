import logging, os, _winreg

def do_config():

    logger = logging.getLogger('de.mineway.emzed')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    op = os.path
    try:
        os.mkdir("logs")
    except:
        pass

    key =_winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                        "Software\\Microsoft\\Windows\\CurrentVersion"
                        "\\Explorer\\User Shell Folders")

    appRoot,_ = _winreg.QueryValueEx(key, "Local AppData")
    appRoot = _winreg.ExpandEnvironmentStrings(appRoot)

    logPath = os.path.join(appRoot, "emzed")
    if not os.path.exists(logPath):
        os.makedirs(logPath)

    fh = logging.FileHandler(os.path.join(logPath, "emzed.log"))
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

    logger.debug("start logging")

