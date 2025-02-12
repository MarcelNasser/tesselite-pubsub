from tesselite.samples import publish
import json
from time import sleep

def encoder():
    # message identifier
    uid = -1
    while True:
        uid += 1
        # message object
        msg = {"uid": uid, "payload": f"( publish ) hello world!"}
        print(f"sent this: {msg}")
        # generating serialized message
        yield json.dumps(msg)
        sleep(2)


if __name__ == '__main__':
    # publishing to the default topic
    publish(broker='kafka', encoder=encoder)

