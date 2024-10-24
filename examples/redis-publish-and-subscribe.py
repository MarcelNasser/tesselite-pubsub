from tesselite.samples import main


def callback(message):
    print(f"received this: {message}")

def encoder():
    import json
    from time import sleep
    for i in range(100):
        msg = {"uid": i, "payload": f"( publish-subscribe ) hello world!"}
        print(f"sent this: {msg}")
        yield json.dumps(msg)
        sleep(1)

if __name__ == '__main__':
    main(broker='redis', callback=callback, encoder=encoder, timeout=3600)

