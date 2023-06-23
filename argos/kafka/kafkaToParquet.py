# pip install ksql
# pip install kafka-python

import concurrent.futures
from kafka import KafkaConsumer

# Create Kafka consumer configuration
consumer_config = {
    'bootstrap_servers': '127.0.0.1:9092',
    'group_id': '1',
    'auto_offset_reset': 'earliest'  # Set the offset to start consuming from
}


# Define a function to process Kafka messages
def process_message(message):
    print(f"Received message: {message.value.decode('utf-8')}")


def listenToCommands(configuration,maxWorkers=6):
    # Create Kafka consumer instance
    consumer = KafkaConsumer(**consumer_config)

    # Subscribe to Kafka topic(s)
    consumer.subscribe(['your_topic'])

    # Create a thread pool executor
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    # Start consuming Kafka messages
    try:
        for message in consumer:
            # Submit the message to the thread pool for processing
            executor.submit(process_message, message)

    except KeyboardInterrupt:
        pass

    finally:
        # Close the Kafka consumer
        consumer.close()
        # Shut down the thread pool executor
        executor.shutdown()
