from time import sleep

from tesselite.samples import consumePublishThread, publish
from tesselite.schemas import Message


def first_message():
    # message with a counter
    yield Message({'count': 1, 'content': 'hello world'}).serialize()


def transform1(message: Message):
    print(f" (worker #1) received this: {message.serialize()}")
    # increment of one
    message.content['count'] += 1
    return message.serialize()


def transform2(message: Message):
    print(f" (worker #2) received this: {message.serialize()}")
    # increment of one
    message.content['count'] -= 1
    return message.serialize()


if __name__ == '__main__':
    # broker
    broker = 'redis'
    # run consumer in background
    thread1 = consumePublishThread(broker=broker, transform=transform1,
                                  topic_in="worker1", topic_out="worker2",
                                  polling_interval=1)
    # run consumer in background
    thread2 = consumePublishThread(broker=broker, transform=transform2,
                                  topic_in="worker2", topic_out="worker1",
                                  polling_interval=1)
    # consume grace
    sleep(2)
    # publish 1 message
    publish(broker=broker, encoder=first_message, topic="worker1")
    # waiting threads
    thread1.join(timeout=360)
    thread2.join(timeout=360)
