import argparse
from argos.kafka import ConsumersHandler
from argos.kafka.processors import SlideProcessor, WindowProcessor
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="The consumers configuration JSON", required=True)
    parser.add_argument("--kafkaHost", dest="kafkaHost", default="localhost")
    parser.add_argument("--projectName", dest="projectName", required=True)
    parser.add_argument("--expConf", dest="expConf", required=True) # , default='/home/eden/Projects.local/2019/DesertWalls/experimentConfiguration.json')
    parser.add_argument("--topic", dest="topic", required=True)
    parser.add_argument("--window", dest="window", required=True)
    parser.add_argument("--slideWindow", dest="slideWindow", required=True)
    args = parser.parse_args()

    with open(args.config, 'r') as configFile:
        consumersConf = json.load(configFile)

    processesDict = consumersConf[args.topic]['processesConfig'][args.window]

    if args.slideWindow != 'None':
        SlideProcessor(args.projectName, args.kafkaHost, args.topic, args.slideWindow, processesDict).start()
    else:
        WindowProcessor(args.projectName, args.kafkaHost, args.expConf, args.topic, args.window, processesDict).start()
