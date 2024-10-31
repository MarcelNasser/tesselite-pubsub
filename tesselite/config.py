import os

from tesselite import App

def load(var):
    try:
        return os.environ[var]
    except KeyError:
         App.Logger.fatal(f"the env variable '{var}' is missing.")
         exit(1)


class RedisEnv:
    HOST = os.environ.get("REDIS_HOST", "localhost")
    PORT = int(os.environ.get("REDIS_PORT", "6379"))
    DB = int(os.environ.get("REDIS_DB", "0"))
    PASSWORD = os.environ.get("REDIS_PASSWORD", "tesselite")
    TOPIC_NAME = 'tesselite-pubsub'
    SUBSCRIPTION_NAME = 'tesselite'


class GCPEnv:
    from dotenv import load_dotenv
    load_dotenv()
    GOOGLE_PROJECT = load('GOOGLE_PROJECT')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    TOPIC_NAME = 'tesselite-pubsub'
    SUBSCRIPTION_NAME = 'tesselite'

class RabbitMQEnv:
    from dotenv import load_dotenv
    load_dotenv()
    HOST = os.environ.get("RABBITMQ_HOST", "localhost")
    PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
    USER = os.environ.get("RABBITMQ_USER", "tesselite")
    PASSWORD = os.environ.get("RABBITMQ_PASSWORD", "tesselite")
    TOPIC_NAME = 'tesselite-pubsub'
    SUBSCRIPTION_NAME = 'tesselite'
    VHOST = '/'



