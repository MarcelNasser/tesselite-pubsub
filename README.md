# tesselite-pubsub
general sugarcoat for all pubsub flavors.

## pubsub
Publish Subscribe is a pretty simple mechanism understandable by any human. 

For example, it is the ruling mechanism of all Social Networks. 

But, yet very complex to code in Python given the variety of backends logic (redis, rabbitMQ, kafka, GCP PubSub, Azure Event Hubs..)

The goal of this library is to streamline the coding of Pubsub in two simple calls:

---
## usage

Available Brokers:

| internal name | official name       | client library                  |
|---------------|---------------------|---------------------------------|
| gcp-pubsub    | Goggle Cloud Pubsub | google-cloud-pubsub = "^2.26.1" |
| redis         | Redis               | redis = "^5.1.1"                |


### low level usage

*consume*

````python
from tesselite.pubsub import pubsubFactory

def callback(message): # callback function inputs serialized message 
    print(f"received this: {message}")
    
# consume loop
with pubsubFactory(broker="gcp-pubsub")(topic="tesselite-pubsub", log_name="consumer") as pubsub:
    pubsub.consume(callback=callback, deadLetter=None, subscription="tesselite")

````

*publish*


````python
from tesselite.pubsub import pubsubFactory

def encoder(): # callback function inputs serialized message 
    yield "hello world"
    
# publish loop
with pubsubFactory(broker="gcp-pubsub")(topic="tesselite-pubsub", log_name="publisher") as pubsub:
    for msg in encoder():
        pubsub.publish(msg)

````


### high level usage

*consume*

````python
from tesselite.samples import consume # importing consume sample


def callback(message): # callback function inputs serialized message 
    print(f"received this: {message}")

if __name__ == '__main__':
    consume(broker='gcp-pubsub', callback=callback) # single-lined consume loop (default topic: tesselite-pubsub
````

*publish*

````python
from tesselite.samples import consume # importing consume sample


def callback(message): # callback function inputs serialized message 
    print(f"received this: {message}")

if __name__ == '__main__':
    consume(broker='gcp-pubsub', callback=callback) # single-lined consume loop (default topic: tesselite-pubsub
````

---

## Behavior

### Best Case Scenario

The interface to all broker backends technology is generic. One would swap seamlessly to any broker technology:

````python
from tesselite import pubsubFactory

# broker : gcp-pubsub
client_gcp = pubsubFactory(broker="gcp-pubsub")(topic="tesselite-pubsub", log_name="tesselite")

# broker : redis
client_redis = pubsubFactory(broker="redis")(topic="tesselite-pubsub", log_name="tesselite")
````

The connection to broker auto-heals when the broker backend is unavailable.

The generic mechanics bellow works for all broker backends:
1. topic checkout
2. topic creation
3. subscription checkout
4. subscription creation
5. publish or consume


### Pathologic Behaviors

A) 
Messages are lost if the subscription doesn't exist →
This is an incurable limitation of pubsub mechanics. 

B) 
The broker `redis` would drop messages if the consumer disconnects →
This seems to be related to 'livestream' behavior of Redis.

C)
The broker `gcp-pubsub` would freeze for a random timeperiod if no messages are available →
This would generate sluggishness from time to time.

Therefore, the broker `redis` is ideal for livestreaming but not for message retention critical PaaS.

Therefore, the broker `gcp-pubsub` is ideal for message retention critical PaaS but maybe sluggish for livestream.
