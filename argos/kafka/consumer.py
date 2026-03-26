"""
Kafka consumer for ingesting device data into Parquet files.

This module provides functions to consume messages from Kafka topics
(one per device type) and write them to Parquet files for offline analysis.
"""

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
    Consume all available messages from a Kafka topic and write to Parquet.

    Connects to Kafka, polls messages until no more are available,
    converts them to a Pandas DataFrame, and writes/appends to a
    Parquet file named ``<topic>.parquet`` in the data directory.

    The data pipeline applies:

    1. JSON deserialization of each message
    2. Timezone-aware datetime column (Israel timezone) from ``timestamp``
    3. Numeric casting for ``Temperature`` and ``RH`` fields
    4. Duplicate removal based on timestamp

    Parameters
    ----------
    topic : str
        The Kafka topic name to consume from (typically a device type name).
    dataDirectory : str
        Directory where the Parquet file will be created/appended.
    """
    max_poll_records = 5000
    logger = logging.getLogger("argos.kafka.kafkaToParquet")
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='127.0.0.1:9092',
        group_id='1',
        auto_offset_reset='earliest',
        max_poll_records=max_poll_records,
        value_deserializer=lambda m: json.loads(m.decode('ascii'))
        # Add more consumer configuration options as needed
    )

    # Consume messages from the topic
    L = []
    keeploop = True
    logger.execution(f"Listening to topic {topic}")
    while keeploop:
        message = consumer.poll(timeout_ms=12000)
        logger.info(f"{topic} - Got {numpy.sum([len(x) for x in message.values()])}  messages.  ")
        totalRecords = 0
        for partitionObj,recordList in message.items():
            frstRcrdTime = recordList[0].value['timestamp']
            lastRcrdTime = recordList[-1].value['timestamp']

            logger.info(
                    f"partition {partitionObj.partition}: From time {pandas.to_datetime(frstRcrdTime, unit='ms')} ({frstRcrdTime}) "
                    f"to {pandas.to_datetime(lastRcrdTime, unit='ms')} ({lastRcrdTime})")

            for record in recordList:
                L.append(record.value)
                logger.debug(f"{topic} - Got message {record.value}")

            totalRecords += len(recordList)

        if totalRecords == 0:
            keeploop = False


    logger.execution(f"Closing consumer")
    consumer.close()

    if len(L) >0:
        logger.execution("Updating parquet")
        fileName = os.path.join(os.path.abspath(dataDirectory),f"{topic}.parquet")

        data = pandas.DataFrame(L)
        if 'timestamp' in data:
            data = data.assign(datetime = data['timestamp'].apply(lambda x: pandas.to_datetime(x,unit="ms").tz_localize('Israel')))
            data = data.sort_values('timestamp').drop_duplicates()

        for field in ['Temperature','RH']:
            if field in data:
                data[field] = data[field].astype(numpy.float64)

        logger.info(f"Updating the {fileName} file")
        if os.path.exists(fileName):
            appendToParquet(fileName,data)
        else:
            writeToParquet(fileName,data)
        logger.info(f"Done. Updated {fileName} for topic {topic}. Last message is at {data.iloc[-1]['datetime']}")

def consume_topic_server(topic, dataDirectory,delayInSeconds):
    """
    Continuously consume from a Kafka topic with periodic polling.

    Runs in an infinite loop, polling the topic and writing data to Parquet.
    Designed for long-running server-mode operation.

    Each cycle:

    1. Polls messages until none are received or 10,000+ accumulated
    2. Commits offsets
    3. Writes/appends to Parquet
    4. If fewer than ``max_poll_records`` received, waits ``delayInSeconds``

    Parameters
    ----------
    topic : str
        The Kafka topic name to consume from.
    dataDirectory : str
        Directory where the Parquet file will be created/appended.
    delayInSeconds : float
        Seconds to wait between poll cycles when data rate is low.
        Checks every 5 seconds during the wait period.
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
        keeploop = True
        totalRecords = 0
        while keeploop:
            message = consumer.poll(timeout_ms=12000)
            logger.info(f"{topic} - Got {numpy.sum([len(x) for x in message.values()])}  messages. ")
            currentMessages = 0
            for partitionObj, recordList in message.items():
                frstRcrdTime = recordList[0].value['timestamp']
                lastRcrdTime = recordList[-1].value['timestamp']

                logger.info(
                    f"partition {partitionObj.partition}: From time {pandas.to_datetime(frstRcrdTime,unit='ms').tz_localize('Israel')} ({frstRcrdTime}) "
                    f"to {pandas.to_datetime(lastRcrdTime,unit='ms').tz_localize('Israel')} ({lastRcrdTime})")
                for record in recordList:
                    L.append(record.value)
                    logger.debug(f"{topic} - Got message {record.value}")

                totalRecords += len(recordList)
                currentMessages = len(recordList)

            if currentMessages == 0 or totalRecords > 10000:
                logger.info(f"{topic} - breaking")
                keeploop = False
            else:
                logger.info(f"{topic} - total records so far: {totalRecords}")


        logger.execution(f"Commiting consumer {topic}")
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
            time.sleep(5)
