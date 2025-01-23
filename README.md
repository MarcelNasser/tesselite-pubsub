# tesselite-pubsub

General sugarcoat for all pubsub flavors.


## purpose
Publish Subscribe is a pretty simple mechanism understandable by any human. For example, it is the ruling mechanism of all social networks. 

But, in Python, pubsub is very complex to code given the variety of broker technologies (redis, rabbitMQ, kafka, GCP PubSub, Azure Event Hubs..)

The purpose of this library is to streamline the coding of Pubsub in a **single-line** call!


## usage

### Available Brokers:

| internal name | official name       | client library                  |
|---------------|---------------------|---------------------------------|
| gcp-pubsub    | Goggle Cloud Pubsub | google-cloud-pubsub = "^2.26.1" |
| redis         | Redis               | redis = "^5.1.1"                |
| rabbitmq      | RabbitMQ            | pika = "^1.3.2"                 |


### Unavailable Brokers:

| internal name | official name       | client library                  |
|---------------|---------------------|---------------------------------|
| kafka         | Apache Kafka        | todo                            |


### low level usage

#### consume

````python
from tesselite.pubsub import pubsubFactory

def callback(message): # callback function inputs serialized message 
    print(f"received this: {message}")
    
# consume loop
with pubsubFactory(broker="gcp-pubsub")(topic="tesselite-pubsub", log_name="consumer") as pubsub:
    pubsub.consume(callback=callback, deadLetter=None, subscription="tesselite")

````

#### publish

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

#### consume

````python
from tesselite.samples import consume # importing consume sample


def callback(message): # callback function inputs serialized message 
    print(f"received this: {message}")

if __name__ == '__main__':
    consume(broker='rabbitmq', callback=callback) # single-lined consume loop (default topic: tesselite-pubsub
````

#### publish

````python
from tesselite.samples import publish # importing publish sample


def encoder(): # callback function inputs serialized message 
    yield "hello"

if __name__ == '__main__':
    publish(broker='rabbitmq', encoder=encoder) # single-lined publish call (default topic: tesselite-pubsub
````


## behavior

### Best Case Scenario

The same programmatic interface is used for all brokers →
One would swap seamlessly to any broker technology by shifting the broker's name:

````python
from tesselite import pubsubFactory

# broker : rabbitmq
client_gcp = pubsubFactory(broker="rabbitmq")(topic="tesselite-pubsub", log_name="tesselite")

# broker : redis
client_redis = pubsubFactory(broker="redis")(topic="tesselite-pubsub", log_name="tesselite")
````

The connection to broker auto-heals when the broker backend is unavailable →
When auto-healing happens the log trace looks like this:
````text
[tesselite][ERROR][2024-10-28 06:22:07] (open) connexion error [ConnectionError] => backoff.
[tesselite][ERROR][2024-10-28 06:22:13] (open) connexion error [ConnectionError] => backoff.
[tesselite][ERROR][2024-10-28 06:22:21] (open) connexion error [ConnectionError] => backoff.
[consume][INFO][2024-10-28 06:22:29] ready.
received this: {"uid": 0, "payload": "( publish ) hello world!"}
received this: {"uid": 1, "payload": "( publish ) hello world!"}
received this: {"uid": 2, "payload": "( publish ) hello world!"}
````

The procedure below is applied seamlessly to all broker technologies →
To guarantee a fail-proof onboarding to the broker:

1. topic checkout
2. topic creation
3. subscription checkout
4. subscription creation
5. publish or consume


### Worst Case Scenario

a. 
Messages are lost if the subscription doesn't exist →
This is an incurable limitation of pubsub mechanics. 

b. 
The broker `redis` would drop messages if the consumer disconnects →
This seems to be related to 'livestream' behavior of Redis.

c.
The broker `gcp-pubsub` would freeze for a random timeperiod if no messages are available →
This would generate sluggishness from time to time.

Therefore, the broker `redis` is ideal for livestreaming but not for message retention critical PaaS.
Therefore, the broker `gcp-pubsub` is ideal for message retention critical PaaS but maybe sluggish for livestream.


![ci](https://github.com/MarcelNasser/tesselite-pubsub/actions/workflows/ci.yml/badge.svg "automated ci")

![cd](https://github.com/MarcelNasser/tesselite-pubsub/actions/workflows/release.yml/badge.svg "automated release")