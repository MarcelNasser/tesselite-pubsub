# tesselite-pubsub
general sugarcoat for all pubsub flavors.

## pubsub
Publish Subscribe is a pretty simple mechanism understandable by any human. 

For example, it is the ruling mechanism of all Social Networks. 

But, yet very complex to code in Python given the variety of backends logic (redis, rabbitMQ, kafka, GCP PubSub, Azure Event Hubs..)

The goal of this library is to streamline the coding of Pubsub in two simple calls:

````python
from tesselite.pubsub import PubSubFactory

````
