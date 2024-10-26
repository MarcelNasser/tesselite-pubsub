import threading
from time import sleep
from typing import Callable, Type

from tesselite import root_logger
from tesselite.exceptions import graceful
from tesselite.pubsub import pubsubFactory
from tesselite.schemas import Message


@graceful
def publish(broker: str, encoder: Callable, topic: str = None):
    """
    Pattern: publish (topicA)
    :param broker: broker backend (gcp-pubsub or redis)
    :param encoder: message generator function (produces bytes or raw string)
    :param topic:
    :return:
    """
    with pubsubFactory(broker=broker)(topic=topic, log_name="publish") as pubsub:
        for msg in encoder():
            pubsub.publish(msg)


@graceful
def consume(broker: str, callback: Callable, topic: str = None, subscription: str = None):
    """
    Pattern: consume (topicA)
    :param broker:
    :param callback:
    :param topic:
    :param subscription:
    :return:
    """
    with pubsubFactory(broker=broker)(topic=topic, log_name="consume") as pubsub:
        pubsub.consume(callback=callback, deadLetter=None,
                       subscription=subscription)


def autoConsumeTest(broker: str, callback: Callable, encoder: Callable, timeout: int = None,
                    topic: str = None, subscription: str = None) -> (threading.Thread, threading.Thread):
    """
    Pattern: publish (topicA) => consume (topicA)
    :param broker: backend
    :param callback: consume callback
    :param encoder: message create
    :param timeout:
    :param topic: topic's name
    :param subscription: subscription's name
    :return: (thread_1, thread_2) to terminate
    """
    consume_thread = threading.Thread(target=consume, args=(broker, callback, topic, subscription), daemon=True)
    publish_thread = threading.Thread(target=publish, args=(broker, encoder, topic), daemon=True)

    # fire consume
    consume_thread.start()
    # consume grace
    sleep(1)
    # fire publish
    publish_thread.start()

    consume_thread.join(timeout=timeout)
    publish_thread.join(timeout=timeout)

    return consume_thread, publish_thread


@graceful
def consumeAndPublish(broker: str, transform: Callable,
                      topic_in: str, topic_out: str, subscription: str = None,
                      schema: Type[Message] = Message, polling_interval: float = 0.01, ):
    """
    Pattern: consume (topicA) => publish (topicB)
    :param broker: backend (gcp-pubsub or redis)
    :param transform: message transformation
    :param schema: object
    :param topic_in: entry topic's name
    :param topic_out: exit topic's name
    :param subscription: subscription's name
    :param polling_interval: add message time gap to control chaos
    :return: None
    """
    if topic_in == topic_out:
        root_logger.warning("circular consumption detected.")

    with pubsubFactory(broker=broker)(topic=topic_out, log_name="consumeAndPublish") as publisher:
        def callback(message):
            deserialized: schema = schema.deserialize(message)
            sleep(polling_interval)
            publisher.publish(transform(deserialized))

        with pubsubFactory(broker=broker)(topic=topic_in, log_name="consumeAndPublish") as consumer:
            consumer.consume(callback=callback, deadLetter=None,
                             subscription=subscription)


def consumePublishThread(broker: str, transform: Callable,
                         topic_in: str, topic_out: str, subscription: str = None,
                         schema: Type[Message] = Message, polling_interval:float=0.01) -> threading.Thread:
    """
    Pattern: consume (topicA) => publish (topicB)
    :param polling_interval: add message time gap to control chaos
    :param broker: backend (gcp-pubsub or redis)
    :param transform: message transformation
    :param schema: object
    :param topic_in: entry topic's name
    :param topic_out: exit topic's name
    :param subscription: subscription's name
    :return: None
    """
    thread = threading.Thread(target=consumeAndPublish,
                              args=(broker, transform, topic_in, topic_out,
                                    subscription, schema, polling_interval),
                              daemon=True)

    # publish and consume
    thread.start()

    return thread
