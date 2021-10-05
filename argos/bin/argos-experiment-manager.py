#! /usr/bin/env python

import argparse
import os
import json
from argos.manager import experimentSetup
import argos

def parser_download_handler(args):

    if len(args.experimentDirectory) == 0:
        experimentDirectory = os.getcwd()

    elif len(args.experimentDirectory) == 1:
        experimentDirectory = os.path.abspath(args.experimentDirectory[0])
    else:
        raise ValueError(f"must get only one directory!. got {args.experimentDirectory}")



    configurtionFileName = os.path.join(experimentDirectory,"runtimeExperimentData","Datasources_Configurations.json")

    with open(configurtionFileName) as jsonConfFile:
        configurationFile = json.load(jsonConfFile)

    experimentName = configurationFile['experimentName']
    destDir = os.path.join(experimentDirectory,"runtimeExperimentData",experimentName)

    mng = experimentSetup(configurationFile,argos.WEB,experimentDirectory)
    print(f"Downloading experiment {experimentName} into directory {destDir}")
    mng.packExperimentSetup(destDir)

def parser_setup_handler(args):


    if len(args.args) == 1:
        experimentDirectory = os.getcwd()
        inputFormat = args.args[0].lower()

    elif len(args.experimentDirectory) == 2:
        experimentDirectory = os.path.abspath(args.experimentDirectory[0])
        inputFormat = args.args[1].tolower()
    else:
        raise ValueError(f"must get only one directory!. got {args.experimentDirectory}")

    if inputFormat not in [argos.WEB,argos.FILE]:
        raise ValueError(f"Please specify correct input format: {argos.WEB} or {argos.FILE}. Got {inputFormat}")

    configurtionFileName = os.path.join(experimentDirectory,"runtimeExperimentData","Datasources_Configurations.json")

    with open(configurtionFileName) as jsonConfFile:
        configurationFile = json.load(jsonConfFile)

    experimentName = configurationFile['experimentName']
    destDir = os.path.join(experimentDirectory,"runtimeExperimentData")

    mng = experimentSetup(configurationFile,inputFormat)
    print(f"Uploading experiment {experimentName} to Thingsboard")
    print(f"Writing configuration files")
    mng.setupExperiment(destDir)


def parser_mapping_handler(args):


    if len(args.args) == 1:
        experimentDirectory = os.getcwd()
        inputFormat = args.args[0].lower()

    elif len(args.experimentDirectory) == 2:
        experimentDirectory = os.path.abspath(args.experimentDirectory[0])
        inputFormat = args.args[1].tolower()
    else:
        raise ValueError(f"Must get . got {args.experimentDirectory}")

    if inputFormat not in [argos.WEB, argos.FILE]:
        raise ValueError(f"Please specify correct input format: {argos.WEB} or {argos.FILE}. Got {inputFormat}")


    configurtionFileName = os.path.join(experimentDirectory, "runtimeExperimentData",
                                        "Datasources_Configurations.json")

    with open(configurtionFileName) as jsonConfFile:
        configurationFile = json.load(jsonConfFile)

    mng = experimentSetup(configurationFile, inputFormat)

    for imageName,imageData in mng.experiment.imageMap.items():
        print(f"----------------- {imageName} --------------------")
        print(mng.experiment.getImageJSMappingFunction(imageName))


def parser_loadTrial_handler(args):

    if len(args.args) == 1:
        experimentDirectory = os.getcwd()
        inputFormat = args.args[0].lower()

    elif len(args.experimentDirectory) == 2:
        experimentDirectory = os.path.abspath(args.experimentDirectory[0])
        inputFormat = args.args[1].tolower()
    else:
        raise ValueError(f"Must get . got {args.experimentDirectory}")

    if inputFormat not in [argos.WEB, argos.FILE]:
        raise ValueError(f"Please specify correct input format: {argos.WEB} or {argos.FILE}. Got {inputFormat}")


    configurtionFileName = os.path.join(experimentDirectory, "runtimeExperimentData",
                                        "Datasources_Configurations.json")

    with open(configurtionFileName) as jsonConfFile:
        configurationFile = json.load(jsonConfFile)

    trialSetName,trialName = args.trial
    state = args.state.lower()

    if state not in ['design','deploy']:
        raise ValueError(f"The state must be design or deploy. Got {state}")

    mng = experimentSetup(configurationFile, inputFormat)
    mng.loadTrial(trialSetName,trialName,state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_download = subparsers.add_parser('downloadMetadata', help='saves the metadata from the experiment')
    parser_setup = subparsers.add_parser('setupExperiment', help='load devices to Thingsboard,saves configuration files for nodered')
    parser_TBmapping = subparsers.add_parser('makeThingsboardMapping', help='Pring the JS function for mapping')
    parser_loadTrial = subparsers.add_parser('loadTrial', help='Loads the attributes of a device to a trial (either design or deploy)')


    ##### download
    parser_download.add_argument('experimentDirectory',nargs='*',type=str,help='Experiment directory')
    parser_download.set_defaults(func=parser_download_handler)

    ##### setup
    parser_setup.add_argument('args',nargs='+',type=str,help='[Experiment directory] [web/file]')
    parser_setup.set_defaults(func=parser_setup_handler)

    ##### TB mapping
    parser_TBmapping.add_argument('args',nargs='+',type=str,help='[Experiment directory] [web/file]')
    parser_TBmapping.set_defaults(func=parser_mapping_handler)

    ##### load Trial

    parser_loadTrial.add_argument('args',nargs='+',type=str,help='[Experiment directory] [web/file]')
    parser_loadTrial.add_argument('--state',type=str,help='design/deploy',default="deploy")
    parser_loadTrial.add_argument('--trial',nargs='+', type=str, help='[trialSetname] [trial name]')

    parser_loadTrial.set_defaults(func=parser_loadTrial_handler)


    args = parser.parse_args()
    args.func(args)
