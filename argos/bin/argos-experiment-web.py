#! /usr/bin/env python
import json
import argparse
from argos import ExperimentGQL, GQLDataLayer
from argos.kafka import ConsumersHandler
import os
from hera import datalayer

parser = argparse.ArgumentParser()
parser.add_argument('action', metavar='action', type=str, nargs='+',
                    help='the action to perform. Use argos-experiment-web help for further information')

parser.add_argument("--expConf", dest="expConf", help="The experiment configurations", required=True)
#parser.add_argument("load", metavar="load", nargs=2, default=None, help="Loads a given trial: {trialSetName} {trialName}")
#parser.add_argument("--runConsumers", dest="runConsumers", default=None, help="Run the kafka consumers. Need to deliever {defaultDataSaveFolder}")
#parser.add_argument("--finalize", dest="finalize", action='store_true', default=False, help="Updating the mongo documents desc with the attributes from the graphQL")
# add finalize - updates the attributes to the mongo desc

args = parser.parse_args()

with open(args.expConf, 'r') as myFile:
    expConf = json.load(myFile)

print(args.action[0])

if args.action[0] =="setup":
    ExperimentGQL(expConf=expConf).setup()
elif args.action[0] =="load":
    ExperimentGQL(expConf=expConf).loadTrial(args.load[0], args.load[1])
elif args.action[0]=="runConsumers":
    graphqlConf = expConf['graphql']
    gqlDL = GQLDataLayer(graphqlConf['url'], graphqlConf['token'])
    experimentName = expConf['name']
    consumersConf = expConf['kafka']['consumers']
    ConsumersHandler(projectName=experimentName,
                     kafkaHost=expConf['kafka']['ip'],
                     tbConf=expConf['thingsboard'],
                     config=gqlDL.getKafkaConsumersConf(expConf['name'], consumersConf),
                     defaultSaveFolder=args.runConsumers,
                     ).run()
elif args.action[0]=="finalize":
    graphqlConf = expConf['graphql']
    gqlDL = GQLDataLayer(graphqlConf['url'], graphqlConf['token'])
    experimentName = expConf['name']
    finalizeConf = gqlDL.getFinalizeConf(experimentName=experimentName)
    for deviceName, deviceDesc in finalizeConf.items():
        doc = datalayer.Measurements.getDocuments(projectName=experimentName, deviceName=deviceName)
        doc['desc'].update(deviceDesc)
        doc.save()
elif args.action[0] =="dumpDevices":
    ExperimentGQL(expConf=expConf).dumpExperimentDevices(args.action[1])
else:
    print("Action must be: ")
    print("\t setup")
    print("\t load [trialSetName] [trialName]")
    print("\t dump [filename]")
    print("\t runConsumers")
    print("\t dumpDevices")
    print("\t finalize")


