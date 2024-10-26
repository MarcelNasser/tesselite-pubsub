"""
Handle messaging (publish/consume)
"""
import abc
import os
from typing import Union
import redis
from dotenv import load_dotenv
from typing import Callable

from google.api_core import exceptions as google_api_core_exceptions
from google.cloud.pubsub_v1 import PublisherClient
from google.cloud.pubsub_v1 import SubscriberClient
import socket

from tesselite import GCPEnv, root_logger
from tesselite.exceptions import connexion
from tesselite.exceptions import MessageProcessingException

# Select broker's type
load_dotenv()
BROKER = os.environ.get("BROKER", "GCP_PUBSUB")


class Pubsub(abc.ABC):
    """
    Publish messages into a Broker
    """

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @abc.abstractmethod
    def open(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def publish(self, msg: str):
        raise NotImplementedError()

    @abc.abstractmethod
    def consume(self, callback: Callable, deadLetter: str, **kwargs):
        raise NotImplementedError()


class RedisPubsub(Pubsub):

    def __init__(self, topic: str, log_name: str = "redis-pubsub"):
        from tesselite import Logger
        self.logger = Logger(log_name)
        self.log_name = log_name
        from tesselite import RedisEnv
        self.logger.debug("loading ..")
        self._pubsub = None
        self._env = RedisEnv()
        self._client = None
        self._topic = topic if topic else self._env.TOPIC_NAME
        self.logger.debug("\n"
                          f"\tBROKER: REDIS\n"
                          f"\tHOST: {self._env.HOST}\n"
                          f"\tPORT: {self._env.PORT}\n"
                          f"\tPASSWORD: "
                          f"( {'hidden' if self._env.PASSWORD else 'empty'} )")

    @property
    def topic(self):
        return self._topic

    @connexion(expected_errors=(socket.gaierror, redis.exceptions.ConnectionError,))
    def open(self):
        self.logger.debug("connecting ..")
        self._client = redis.Redis(host=self._env.HOST, port=self._env.PORT,
                                   db=self._env.DB, password=self._env.PASSWORD)
        self.logger.debug("pinging ..")
        self._client.ping()
        self.logger.info("ready.")

    def close(self):
        self._client.close()
        self.logger.info("terminated.")

    # if standard networks errors, backoff the loop
    @connexion(expected_errors=(socket.gaierror, redis.exceptions.ConnectionError,))
    def publish(self, msg: str):
        self._client.publish(self._topic, msg)

    # consume loop
    # if standard networks errors, backoff the loop
    @connexion(expected_errors=(socket.gaierror, redis.exceptions.ConnectionError,))
    def consume(self, callback: Callable, deadLetter: str = None, **kwargs):
        self.logger.debug("consuming ..")

        """
        callback: function called with message payload
        e.g.,
            def callback(message: str):
                print(message)
        deadLetter: a backup topic where unconsumed events are pushed
        """
        # only events happening after subscription are processed
        self._pubsub: redis.client.PubSub = self._client.pubsub(ignore_subscribe_messages=False)
        self._pubsub.subscribe(self._topic)

        # exec wrapper
        @connexion(expected_errors=(socket.gaierror, redis.exceptions.ConnectionError,))
        def exec_callback(message):
            if message['type'] == 'message':
                data = msg['data'].decode()
                callback(data)

        # event loop
        try:
            for msg in self._pubsub.listen():
                try:
                    exec_callback(msg)
                except Exception as err:
                    self.logger.error(err, stack_info=True)
                    if deadLetter:
                        self._client.publish(deadLetter, msg)
                    raise
        except KeyboardInterrupt:
            self.logger.info("graceful exit")
        except Exception:
            raise


class GCPPubSub(Pubsub):

    def __init__(self, topic: str, log_name: str = "pubsub-gcp"):
        from tesselite import Logger
        self.logger = Logger(log_name)
        self._topic_path = None
        self.logger.debug("loading ..")
        self._env = GCPEnv()
        self._topic = topic if topic else self._env.TOPIC_NAME
        self._topic_path = None
        self._subscription = self._env.SUBSCRIPTION_NAME
        self._subscription_path = None
        self._publisher_client = None
        self._subscriber_client = None
        self.logger.debug("\n"
                          f"\tBROKER: GCP\n"
                          f"\tPROJECT: {self._env.GOOGLE_PROJECT}\n"
                          f"\tTOPIC: {self._topic}\n"
                          f"\tCREDENTIALS: "
                          f"( {'hidden' if self._env.GOOGLE_APPLICATION_CREDENTIALS else 'empty'} )")

    @property
    def topic(self):
        return self._topic

    def open(self):
        self._publisher_client = PublisherClient()
        # set topic location
        self._topic_path = self._publisher_client.topic_path(self._env.GOOGLE_PROJECT, self.topic)
        # check topic
        self.check_topic()
        self.logger.info("ready.")

    def close(self):
        self._publisher_client.__exit__(None, None, None)
        if self._subscriber_client is not None:
            self._subscriber_client.__exit__(None, None, None)
        self.logger.info("terminated.")

    @connexion(
        expected_errors=(google_api_core_exceptions.ServiceUnavailable, google_api_core_exceptions.Forbidden),
        noisy_errors=(google_api_core_exceptions.AlreadyExists,)
    )
    def check_topic(self):
        """
        creates a new topic if it doesn't exist
        in production, Terraform must create topics
        """
        try:
            self.logger.debug(f"checking  .. topic={self._topic_path}")
            self._publisher_client.get_topic(topic=self._topic_path, retry=None)
        except google_api_core_exceptions.NotFound:
            self.logger.info(f"creating new topic .. {self._topic_path}")
            self._publisher_client.create_topic(name=self._topic_path)
        except google_api_core_exceptions.Forbidden as err:
            self.logger.error(f"checking topic .. {self._topic_path} failed => reason:forbidden.")
            self.logger.error(err)
        except:
            raise

    @connexion(
        expected_errors=(google_api_core_exceptions.ServiceUnavailable, google_api_core_exceptions.Forbidden),
        noisy_errors=(google_api_core_exceptions.AlreadyExists,)
    )
    def check_subscription(self):
        """
        creates a new subscription if it doesn't exist
        in production, Terraform must create subscriptions for better retention
        """
        # check topic
        self.check_topic()
        try:
            self.logger.debug(f"checking subscription .. {self._subscription_path}")
            resource = self._subscriber_client.get_subscription(subscription=self._subscription_path)
            self.logger.debug(f"name={resource.name}, topic={resource.topic}")
            if resource.topic != self._topic_path:
                self.logger.fatal("\n"
                                  "\tdetected inconsistent subscription ..\n"
                                 f"\t* consumer's topic: {self._topic_path}\n"
                                 f"\t* subscription's topic: {resource.topic}")
                exit(1)
            return
        except (google_api_core_exceptions.NotFound, google_api_core_exceptions.InvalidArgument):
            self.logger.info(f"registering new subscription .. {self._subscription_path}")
            self._subscriber_client.create_subscription(name=self._subscription_path, topic=self._topic_path)
        except google_api_core_exceptions.Forbidden as err:
            self.logger.error(f"registering subscription .. {self._subscription_path} failed => reason:forbidden.")
            self.logger.error(err)
        except Exception as err:
            self.logger.error(err, stack_info=True)
            raise

    @connexion(
        expected_errors=(google_api_core_exceptions.ServiceUnavailable,),
        noisy_errors=(google_api_core_exceptions.AlreadyExists,)
    )
    def publish(self, msg: str):
        call = self._publisher_client.publish(self._topic_path, msg.encode() if isinstance(msg, str) else msg)
        return call.result()

    @connexion(expected_errors=(google_api_core_exceptions.ServiceUnavailable,
                                google_api_core_exceptions.RetryError),
               noisy_errors=(
               google_api_core_exceptions.AlreadyExists, google_api_core_exceptions.NotFound, TimeoutError)
               )
    def consume(self, callback: Callable, subscription: str = None, deadLetter: str = None):
        """
        callback: function called with message payload
        deadLetter: is a backup topic where unconsumed events are pushed
        """

        # exec wrapper
        @connexion(expected_errors=(google_api_core_exceptions.ServiceUnavailable,
                                    MessageProcessingException, google_api_core_exceptions.NotFound,))
        def exec_callback(message):
            try:
                callback(message.data.decode())
                message.ack()
            except Exception as err:
                self.logger.error(f"{type(err)} {err}")
                raise MessageProcessingException()

        # event loop
        with SubscriberClient() as self._subscriber_client:
            # check subscription
            self.logger.debug("checking ..")
            self._subscription = subscription if subscription is not None else self._env.SUBSCRIPTION_NAME
            # append topic name to create 1:1 mapping with topic
            self._subscription = self._subscription+ '-' + self._topic
            self._subscription_path = self._subscriber_client.subscription_path(subscription=self._subscription,
                                                                                project=self._env.GOOGLE_PROJECT)
            self.check_subscription()
            self.logger.debug("start consuming ..")
            future = self._subscriber_client.subscribe(subscription=self._subscription_path,
                                                       callback=exec_callback,
                                                       use_legacy_flow_control=True)
            try:
                future.result()
            except KeyboardInterrupt:
                future.cancel()
            except Exception:
                raise


def pubsubFactory(broker: str = BROKER) -> Union[type(RedisPubsub), type(GCPPubSub)]:
    """creates a publisher object
    :type broker: str: broker backend.
        supported:
          - redis
          - gcp-pubsub
    """
    if broker.upper() == "REDIS":
        return RedisPubsub
    elif broker.upper() == "GCP-PUBSUB":
        return GCPPubSub
    else:
        root_logger.fatal(f"Broker type <{BROKER}> not available yet.")
        exit(1)
