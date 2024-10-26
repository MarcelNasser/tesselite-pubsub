from tesselite.samples import consume # importing consume sample


def callback(message): # callback function inputs serialized message
    print(f"received this: {message}")

if __name__ == '__main__':
    consume(broker='redis', callback=callback) # single-lined consume loop (default topic: tesselite-pubsub
