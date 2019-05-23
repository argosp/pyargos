import json
import argparse
import pyargos.thingsboard as tb

parser = argparse.ArgumentParser()
parser.add_argument("--connection",dest="connectConf" ,help="The connection file",required=True)
parser.add_argument("--confJson",dest="trialConf" ,help="A JSON with the trial configuration",required=True)
args = parser.parse_args()

with open(args.trialConf,"r") as trialFile:
    trialConfig = json.load(trialFile)

with open(args.connectConf,"r") as connectFile:
    connection = json.load(connectFile)
tbh = tb.tbHome(connection)

def defineTrial(config):
    trialTemplate = {}
    trialTemplate['properties'] = config['properties']
    # trialTemplate['DEVICES'] = {}
    # trialTemplate['ASSETS'] = {}
    for entitiesCreation in config['Entities']:
        typeKey = entitiesCreation['entityType'] + 'S'

        if typeKey not in trialTemplate.keys():
            trialTemplate[typeKey] = {}

        if entitiesCreation['Number'] == 1:
            trialTemplate[typeKey][entitiesCreation['Name']] = {'attributes': {'longitude':0, 'latidude':0}}
        else:
            for entityNum in range(entitiesCreation['Number']):
                trialTemplate[typeKey][entitiesCreation['Name']+str(entityNum+1)] = {'attributes': {'longitude':0, 'latidude':0}}
    return trialTemplate

def loadTrial(template):


    return

with open('trialTemplate.json', 'w') as trialTemplateJSON:
    json.dump(defineTrial(trialConfig),trialTemplateJSON, indent=4, sort_keys=True)

with open('trialTemplate.json', 'r') as trialTemplate:
    loadTrial(trialTemplate)