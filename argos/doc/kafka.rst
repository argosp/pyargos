.. _kafkaPage:

Kafka
*****




Installation
-----------------------------

Install the kafka/zooker.

Install the 'ksqlDB https://docs.ksqldb.io/en/latest/operate-and-deploy/installation/installing' using docker:

::
    docker pull confluentinc/ksqldb-server

Its useful to install the ksqldb-cli as well:

::
    docker pull confluentinc/ksqldb-cli

Make sure that the kafka is up (with zookeeper).

Creating the management topic
-----------------------------

Generally, we do not jhave to create the topics. However, this is a good verification
that the server is up and running.

::

    <path-to-confluent>/bin/kafka-topics.sh --create --topic argosManagement  --bootstrap-server 127.0.0.1:9092


Listing the topics
------------------

::

    <path-to-confluent>/bin/kafka-topics.sh --list  --bootstrap-server 127.0.0.1:9092


Sending and recieving messages using the command-line
-----------------------------------------------------

To send a free text message type

::

     <path-to-confluent>/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic argosManagement

And then type you messages. Alternatively, you can use < redirection to send a file:

::

     <path-to-confluent>/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic argosManagement < inFile

To print the messages that were revceived (good for debugging):

::

     <path-to-confluent>/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic argosManagement


