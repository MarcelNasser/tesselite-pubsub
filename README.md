# tesselite-pubsub
general sugarcoat for all pubsub flavors.

## pubsub
Publish Subscribe is a pretty simple mechanism understandable by any human. 

For example, it is the ruling mechanism of all Social Networks. 

But, yet very complex to code in Python given the variety of backends logic (redis, rabbitMQ, kafka, GCP PubSub, Azure Event Hubs..)

The goal of this library is to streamline the coding of Pubsub in two simple calls:

---
## usage



### low level usage

````python
from tesselite.pubsub import pubsubFactory

def callback(message): # callback function inputs serialized message 
    print(f"received this: {message}")
    
# consume loop
with pubsubFactory(broker="gcp-pubsub")(topic="tesselite-pubsub", log_name="consumer") as pubsub:
    pubsub.consume(callback=callback, deadLetter=None, subscription="tesselite")

````


### high level usage

````python
from tesselite.samples import consume # importing consume sample


def callback(message): # callback function inputs serialized message 
    print(f"received this: {message}")

if __name__ == '__main__':
    consume(broker='gcp-pubsub', callback=callback) # single-lined consume loop (default topic: tesselite-pubsub
````
