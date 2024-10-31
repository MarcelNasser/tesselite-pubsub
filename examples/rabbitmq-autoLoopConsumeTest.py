from time import sleep

from tesselite.samples import consumePublishThread, publish
from tesselite.schemas import Message


def first_message():
    # message with a counter
    yield Message({'count': 0, 'content': 'hello world'}).serialize()


def transform(message: Message):
    print(f"received this: {message.serialize()}")
    # increment of one
    message.content['count'] += 1
    return message.serialize()


if __name__ == '__main__':
    broker = 'rabbitmq'
    # run consumer in background
    thread = consumePublishThread(broker=broker, transform=transform,
                                  topic_in="tesselite-test", topic_out="tesselite-test",
                                  polling_interval=1)
    # consume grace
    sleep(1)
    # publish 1 message
    publish(broker=broker, encoder=first_message, topic="tesselite-test")
    thread.join(timeout=360)
