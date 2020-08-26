import argparse
from argos.kafka import SimpleProcessor
import json
from multiprocessing import Pool


def startProcesses(projectName, kafkaHost, topic, window, slide, processesDict, expConf):
    SimpleProcessor(projectName, kafkaHost, topic, window, slide, processesDict, expConf).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="The consumers configuration JSON", required=True)
    parser.add_argument("--kafkaHost", dest="kafkaHost", default="localhost")
    parser.add_argument("--projectName", dest="projectName", required=True)
    parser.add_argument("--expConf", dest="expConf", default='/home/eden/Projects.local/2019/DesertWalls/experimentConfiguration.json')
    args = parser.parse_args()

    with open(args.config) as configFile:
        config = json.load(configFile)

    poolNum = 0
    for topic, topicDict in config.items():
        for window, windowDict in topicDict.items():
            for slide, slideDict in windowDict.items():
                poolNum += len(slideDict)

    with Pool(poolNum) as p:
        startProcessesInputs = []
        for topic, topicDict in config.items():
            for window, windowDict in topicDict.items():
                window = None if window=='None' else int(window)
                for slide, slideDict in windowDict.items():
                    slide = None if slide=='None' else int(slide)
                    startProcessesInputs.append((args.projectName, args.kafkaHost, topic, window, slide, slideDict, args.expConf))
        print('---- ready ----')
        p.starmap(startProcesses, startProcessesInputs)
