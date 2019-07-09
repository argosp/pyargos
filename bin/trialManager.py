import json
import argparse
from pyargos.experimentManagement import Experiment

parser = argparse.ArgumentParser()
parser.add_argument("--expConf", dest="expConf" , help="The Experiment configuration JSON", required=True)
parser.add_argument("--setup", dest="setupFlag", action='store_true', default=False, help="Setup the experiment")
parser.add_argument("--load", dest="loadName", default=None, help="Loads a given trial")
parser.add_argument("--updateAttr", dest="attrJSON", default=None, help='Update attributs according to a given JSON')
args = parser.parse_args()

with open(args.expConf,"r") as expConf:
    config = json.load(expConf)

exp = Experiment(config)

if args.setupFlag:
    exp.setup()

if args.loadName is not None:
    exp.loadTrial(args.loadName)

if args.attrJSON is not None:
    with open(args.attrJSON, 'r') as jsonFile:
        attrJSON = json.load(jsonFile)
    for trialName, updateList in attrJSON.items():
        for updateJSON in updateList:
            if 'updateLevel' in updateJSON.keys():
                exp.setAttributesInTrial(trialName, updateJSON['entityType'], updateJSON['entityName'],
                                         updateJSON['entityType'], updateJSON['attrMap'], updateJSON['updateLevel'])
            else:
                exp.setAttributesInTrial(trialName, updateJSON['entityType'], updateJSON['entityName'],
                                         updateJSON['entityType'], updateJSON['attrMap'])