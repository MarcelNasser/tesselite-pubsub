from tesselite.samples import consume


def callback(message):
    print(f"received this: {message}")

if __name__ == '__main__':
    consume(broker='gcp_pubsub', callback=callback)
