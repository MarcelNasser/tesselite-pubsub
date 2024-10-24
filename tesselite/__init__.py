# High-Level Setters
import logging
import os
import sys

from tesselite.exceptions import ConfigurationException

APPLICATION_NAME = "tesselite"


class Logger(logging.Logger):

    def __init__(self, name=APPLICATION_NAME):
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


root_logger = Logger(APPLICATION_NAME)


def load(var):
    try:
        return os.environ[var]
    except KeyError:
         root_logger.fatal(f"the env variable '{var}' is missing.")
         exit(1)


class RedisEnv:
    from dotenv import load_dotenv
    load_dotenv()
    HOST = os.environ.get("REDIS_HOST", "localhost")
    PORT = int(os.environ.get("REDIS_PORT", "6379"))
    DB = int(os.environ.get("REDIS_DB", "0"))
    PASSWORD = os.environ.get("REDIS_PASSWORD", "")
    TOPIC_NAME = 'tesselite-pubsub'


class GCPEnv:
    from dotenv import load_dotenv
    load_dotenv()
    GOOGLE_PROJECT = load('GOOGLE_PROJECT')
    GOOGLE_APPLICATION_CREDENTIALS = load('GOOGLE_APPLICATION_CREDENTIALS')
    TOPIC_NAME = 'tesselite-pubsub'
    SUBSCRIPTION_NAME = 'tesselite'
