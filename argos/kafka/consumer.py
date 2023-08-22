import os.path
import time
import numpy
import json
from argos.utils.parquetUtils import writeToParquet,appendToParquet

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
        max_poll_records=10000,
        value_deserializer=lambda m: json.loads(m.decode('ascii'))
        # Add more consumer configuration options as needed
    )

    # Consume messages from the topic
    L = []
    logger.execution(f"Listening to topic {topic}")
    message = consumer.poll(timeout_ms=12000)
    logger.info(f"{topic} - Got {numpy.sum([len(x) for x in message.values()])}  messages.  ")
    for partitionObj,recordList in message.items():
        frstRcrdTime = recordList[0].value['timestamp']
        lastRcrdTime = recordList[-1].value['timestamp']

        logger.info(
            f"partition {partitionObj.partition}: From time {pandas.to_datetime(frstRcrdTime, unit='ms')} ({frstRcrdTime}) "
            f"to {pandas.to_datetime(lastRcrdTime, unit='ms')} ({lastRcrdTime})")
        for record in recordList:
            L.append(record.value)
            logger.debug(f"{topic} - Got message {record.value}")

    logger.execution(f"Closing consumer")
    consumer.close()

    if len(L) >0:
        logger.execution("Updating parquet")
        fileName = os.path.join(os.path.abspath(dataDirectory),f"{topic}.parquet")

        data = pandas.DataFrame(L)
        data = data.assign(datetime = data['timestamp'].apply(lambda x: pandas.to_datetime(x,unit="ms").tz_localize('Israel')))
        data = data.sort_values('timestamp')

        logger.info(f"Updating the {fileName} file")
        if os.path.exists(fileName):
            appendToParquet(fileName,data)
        else:
            writeToParquet(fileName,data)
        logger.info(f"Done. Updated {fileName} for topic {topic}. Last message is at {data.iloc[-1]['datetime']}")

def consume_topic_server(topic, dataDirectory,delayInSeconds):
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
    mxRcrd = 5000
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='127.0.0.1:9092',
        group_id='1',
        auto_offset_reset='earliest',
        max_poll_records=mxRcrd,
        value_deserializer=lambda m: json.loads(m.decode('ascii'))
        # Add more consumer configuration options as needed
    )

    while True:
        # Consume messages from the topic
        L = []
        logger.execution(f"Listening to topic {topic}")
        message = consumer.poll(timeout_ms=12000)
        logger.info(f"{topic} - Got {numpy.sum([len(x) for x in message.values()])}  messages.  ")
        for partitionObj, recordList in message.items():
            frstRcrdTime = recordList[0].value['timestamp']
            lastRcrdTime = recordList[-1].value['timestamp']

            logger.info(
                f"partition {partitionObj.partition}: From time {pandas.to_datetime(frstRcrdTime,unit='ms').tz_localize('Israel')} ({frstRcrdTime}) "
                f"to {pandas.to_datetime(lastRcrdTime,unit='ms').tz_localize('Israel')} ({lastRcrdTime})")
            for record in recordList:
                L.append(record.value)
                logger.debug(f"{topic} - Got message {record.value}")

        logger.execution(f"Commiting consumer")
        consumer.commit()


        if len(L) > 0:
            logger.execution("Updating parquet")
            fileName = os.path.join(os.path.abspath(dataDirectory), f"{topic}.parquet")

            data = pandas.DataFrame(L)
            data = data.assign(datetime=data['timestamp'].apply(lambda x: pandas.to_datetime(x,unit="ms").tz_localize('Israel')))
            data = data.sort_values('timestamp')

            logger.info(f"Updating the {fileName} file")
            if os.path.exists(fileName):
                appendToParquet(fileName, data)
            else:
                writeToParquet(fileName, data)
            logger.info(f"Done. Updated {fileName} for topic {topic}. Last message is at {data.iloc[-1]['datetime']}")

        if len(L) >= mxRcrd:
            logger.execution(f"Got more than the maximum ({mxRcrd}). Polling again")
            continue
        else:
            logger.execution(f"Got less than the maximum ({mxRcrd}). Waiting...")

        logger.info(f"Topic {topic}: Waiting for {delayInSeconds} seconds, check every 5s")
        for i in range(int(delayInSeconds/5)+1):
            logger.info(f"Topic {topic}:  Waiting for {i*5} sec out of {delayInSeconds}")
            # activation = consumer.poll()
            # if numpy.sum([len(x) for x in activation.values()]) > 0:
            #     logger.info(f"Topic {topic}: Got reuest for consume")
            #     break
            time.sleep(5)



    #
    # for msg in L:
    #     print(f"Received message: {msg}")
#
#thread1 = threading.Thread(target=consume_topic, args=('Sonic',"data"))
#thread2 = threading.Thread(target=consume_topic, args=('TTT',"data"))
#
#thread1.start()
#thread2.start()
#
# # Wait for the threads to finish
#thread1.join()
#thread2.join()
