import threading
from typing import Callable

from tesselite.exceptions import graceful
from tesselite.pubsub import pubsubFactory



@graceful
def publish(broker:str, encoder:Callable, topic=None):
    with pubsubFactory(broker=broker)(topic=topic, log_name="publisher") as pubsub:
        for msg in encoder():
            pubsub.publish(msg)

@graceful
def consume(broker:str, callback:Callable, topic=None, subscription=None):
    """consume loop"""
    with pubsubFactory(broker=broker)(topic=topic, log_name="consumer") as pubsub:
        pubsub.consume(callback=callback, deadLetter=None,
                       subscription=subscription)


def main(broker:str=None, callback:Callable=None, encoder:Callable=None, timeout=30,
         topic:str=None, subscription:str=None):
    consume_thread = threading.Thread(target=consume, args=(broker, callback, topic, subscription), daemon=True)
    publish_thread = threading.Thread(target=publish, args=(broker, encoder, topic), daemon=True)

    consume_thread.start()
    publish_thread.start()

    consume_thread.join(timeout=timeout)
    publish_thread.join(timeout=timeout)



