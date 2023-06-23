import os.path

import numpy
import json
from argos.utils.parquetUtils import writeToParquet,appendToParquet

import threading

import pandas

from kafka import KafkaConsumer
import logging

def consume_topic(topic,dataDirectory):
    """
        Reads from the kafka topic and saves the data back to the
    Parameters
    ----------
    topic
    frequency : float
            The number of messages that the devices emits every second.
            used to estimate the number of messages we have to retrieve
    dataDirectory

    Returns
    -------

    """
    logger = logging.getLogger("argos.kafka.kafkaToParquet")
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='127.0.0.1:9092',
        group_id='1',
        auto_offset_reset='earliest',
        max_poll_records=12000,
        value_deserializer=lambda m: json.loads(m.decode('ascii'))
        # Add more consumer configuration options as needed
    )

    # Consume messages from the topic
    L = []
    logger.execution(f"Listening to {topic}")
    message = consumer.poll(timeout_ms=1000)
    logger.info(f"{topic} - Got {numpy.sum([len(x) for x in message.values()])}  messages.  ")
    for partitionObj,recordList in message.items():
        frstRcrdTime = recordList[0].value['datetime']
        lastRcrdTime = recordList[-1].value['datetime']

        logger.info(f"partition {partitionObj.partition}: From time {pandas.to_datetime(frstRcrdTime)} ({frstRcrdTime}) "
                    f"to {pandas.to_datetime(lastRcrdTime)} ({lastRcrdTime})")
        for record in recordList:
            L.append(record.value)
            logger.debug(f"{topic} - Got message {record.value}")

    consumer.close()

    if len(L) >0:
        logger.execution("Updating parquet")
        fileName = os.path.join(os.path.abspath(dataDirectory),f"{topic}.parquet")

        data = pandas.DataFrame(L)
        data = data.assign(datetime = data['datetime'].apply(lambda x: pandas.to_datetime(x).tz_localize('Israel')))

        logger.info(f"Updating the {fileName} file")
        if os.path.exists(fileName):
            appendToParquet(fileName,data)
        else:
            writeToParquet(fileName,data)
        logger.info(f"Done. Updated {fileName} for topic {topic}. Last message is at {data.iloc[-1]['datetime']}")

    #
    # for msg in L:
    #     print(f"Received message: {msg}")

thread1 = threading.Thread(target=consume_topic, args=('Sonic',"data"))
#thread2 = threading.Thread(target=consume_topic, args=('GC',))

thread1.start()
#thread2.start()

# Wait for the threads to finish
thread1.join()
#thread2.join()
