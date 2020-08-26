import argparse
from argos.kafka import ProjectProcessor
import json


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="The consumers configuration JSON", required=True)
    parser.add_argument("--kafkaHost", dest="kafkaHost", default="localhost")
    parser.add_argument("--projectName", dest="projectName", required=True)
    parser.add_argument("--expConf", dest="expConf", default='/home/eden/Projects.local/2019/DesertWalls/experimentConfiguration.json')
    args = parser.parse_args()

    with open(args.config) as configFile:
        consumersConf = json.load(configFile)

    projectProcessor = ProjectProcessor(args.projectName, args.kafkaHost, args.expConf, consumersConf)

    projectProcessor.start()
