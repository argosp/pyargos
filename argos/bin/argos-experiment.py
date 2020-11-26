import json
import argparse
from argos import ExperimentGQL, GQLDataLayer
from argos.kafka import ConsumersHandler
import os

parser = argparse.ArgumentParser()
parser.add_argument("--expConf", dest="expConf", help="The experiment configurations", required=True)
parser.add_argument("--setup", dest="setup", action='store_true', default=False, help="Setup the experiment")
parser.add_argument("--load", dest="load", nargs=2, default=None, help="Loads a given trial: {trialSetName} {trialName}")
parser.add_argument("--runConsumers", dest="runConsumers", default=None, help="Run the kafka consumers. Need to deliever {defaultDataSaveFolder}")

args = parser.parse_args()

with open(args.expConf, 'r') as myFile:
    expConf = json.load(myFile)

if args.setup:
    ExperimentGQL(expConf=expConf).setup()

if args.load is not None:
    ExperimentGQL(expConf=expConf).loadTrial(args.load[0], args.load[1])

if args.runConsumers is not None:
    graphqlConf = expConf['graphql']
    gqlDL = GQLDataLayer(graphqlConf['url'], graphqlConf['token'])
    experimentName = expConf['name']
    consumersConf = expConf['kafka']['consumers']
    ConsumersHandler(projectName=experimentName,
                     kafkaHost=expConf['kafka']['ip'],
                     tbConf=expConf['thingsboard'],
                     config=gqlDL.getKafkaConsumersConf(expConf['name'], consumersConf),
                     defaultSaveFolder=os.path.join(os.path.expanduser('~'), 'data'),
                     ).run()