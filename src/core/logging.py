import logging
import sys
#Importing modules
def setup_logging() -> None:
    #Root Logger for the entre project
    logging.basicConfig(
        level = logging.DEBUG,
        format = "[%(levelname)s] [%(asctime)s] [%(module)s] - %(message)s",
        datefmt = "%H:%M:%S",#Hour,minute,seconds
        handlers=[logging.StreamHandler(sys.stdout)]
    )