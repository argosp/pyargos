import os
import json
from .manager import experimentSetup
import argos
import logging


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

    mng = experimentSetup(configurationFile,argos.WEB)
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
    print("...Done")


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
