from tesselite.samples import publish
import json
from time import sleep

def encoder():

    uid = -1

    while True:
        uid += 1
        msg = {"uid": uid, "payload": f"( publish ) hello world!"}
        print(f"sent this: {msg}")
        yield json.dumps(msg)
        sleep(2)


if __name__ == '__main__':
    publish(broker='redis', encoder=encoder)

