import json
import argparse
from pyargos.experimentManagement import Experiment

parser = argparse.ArgumentParser()
parser.add_argument("--expConf", dest="expConf" , help="The Experiment configuration JSON", required=True)
parser.add_argument("--setup", dest="setupFlag", action='store_true', default=False, help="Setup action")
parser.add_argument("--load", dest="loadName", default=None, help="--load [trialName] : Loads the trial [trialName]")
args = parser.parse_args()

with open(args.expConf,"r") as expConf:
    config = json.load(expConf)

exp = Experiment(config)

if args.setupFlag:
    exp.setup()

if args.loadName is not None:
    exp.loadTrial(args.loadName)