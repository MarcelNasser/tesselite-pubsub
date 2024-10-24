from tesselite.samples import main
import json
from time import sleep

def callback(message):
    print(f"received this: {message}")

def encoder():

    for i in range(100):
        msg = {"uid": i, "payload": f"( publish-subscribe ) hello world!"}
        print(f"sent this: {msg}")
        yield json.dumps(msg).encode()
        sleep(5)

if __name__ == '__main__':
    main(broker='gcp-pubsub', callback=callback, encoder=encoder, timeout=3600)

