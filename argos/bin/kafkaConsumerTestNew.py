from kafka import KafkaConsumer
import argparse
from argos.kafka import ConsumerProcessor
import json
from multiprocessing import Pool


def startProcesses(topic, kafkaHost, process, args):
    consumer = KafkaConsumer(topic,
                             bootstrap_servers=kafkaHost,
                             auto_offset_reset='latest',
                             enable_auto_commit=True
                             #group_id=group_id
                             )
    ConsumerProcessor(consumer, process, **args).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config" , help="The configuration JSON", required=True)
    parser.add_argument("--kafkaHost", dest="kafkaHost", default="localhost")
    args = parser.parse_args()

    with open(args.config) as configFile:
        config = json.load(configFile)

    poolNum = 0
    for topic in config:
        for process in config[topic]:
            poolNum += len(config[topic][process])

    consumersDict = {}

    with Pool(poolNum) as p:
        processesInputs = []
        for topic, processesDict in config.items():
            # print(topicConfig['topic'])
            for process, processArgsList in processesDict.items():
                for processArgs in processArgsList:
                    processesInputs.append((topic, args.kafkaHost, process, processArgs))
        # print(processesInputs)
        print('---- ready ----')
        p.starmap(startProcesses, processesInputs)
