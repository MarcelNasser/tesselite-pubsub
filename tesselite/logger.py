import logging
import os
import sys


class Logger(logging.Logger):

    def __init__(self, name):
        super().__init__(name=name)
        self.set_handler()

    def set_handler(self):
        hdr = logging.StreamHandler(sys.stdout)
        # log format
        fmt = logging.Formatter('[%(name)s][%(levelname)s][%(asctime)s] %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
        hdr.setFormatter(fmt)
        # load env vars
        from dotenv import load_dotenv
        load_dotenv()
        # set loglevel
        lvl = os.environ.get('LOGLEVEL', 'ERROR').upper()
        self.setLevel(lvl)
        self.addHandler(hdr)
