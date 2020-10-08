#! /usr/bin/env python

import argparse
from argos.kafka import ConsumersHandler
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="The consumers configuration JSON", required=True)
    parser.add_argument("--kafkaHost", dest="kafkaHost", default="localhost")
    parser.add_argument("--projectName", dest="projectName", required=True)
    parser.add_argument("--expConf", dest="expConf", required=True) # , default='/home/eden/Projects.local/2019/DesertWalls/experimentConfiguration.json')
    args = parser.parse_args()

    ConsumersHandler(projectName=args.projectName,
                     kafkaHost=args.kafkaHost,
                     expConf=args.expConf,
                     config=args.config,
                     runFile=os.path.join(os.path.expanduser('~'), 'Development/pyargos/argos/bin/runTest.py')
                     ).run()
