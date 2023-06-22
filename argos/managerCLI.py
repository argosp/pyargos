import os
import json
from .manager import experimentSetup
import logging


def experiment_createDirectory(arguments):
    logger = logging.getLogger("argos.bin.experiment_createDirectory")
    logger.info("--------- Start ---------")

    experimentDirectory = os.path.abspath(arguments.directory)
    logger.info(f"Creating the experiment {arguments.experimentName} in directory {experimentDirectory}")

    fullDirectory = os.path.join(experimentDirectory,arguments.experimentName)

    logger.execution("Creating experiment directories")
    os.makedirs(os.path.join(fullDirectory,"code"),exist_ok=True)
    os.makedirs(os.path.join(fullDirectory, "data"), exist_ok=True)
    os.makedirs(os.path.join(fullDirectory, "runtimeExperimentData"), exist_ok=True)

    logger.execution("Creating basic Datasources_Configurations.json")
    expDict = dict(experimentName=arguments.experimentName)
    with open(os.path.join(fullDirectory, "runtimeExperimentData","Datasources_Configurations.json"),'w') as confFile:
        json.dump(expDict,confFile,indent=4)

    logger.execution("Creating basic inclusion code file in code")
    argos_basic = f"""
from hera.utils.unum import *
import sys 
import os 
from argos.experimentSetup.dataObjectsFactory import fileExperimentFactory

print("importing pandas")
import pandas 
print("importing numpy")
import pandas 
print("importing matplotlib as plt")
import matplotlib.pyplot as plt  


{arguments.experimentName} = fileExperimentFactory("{fullDirectory}").getExperiment()
print("Experiment loaded into variable {arguments.experimentName} ")  
"""
    with open(os.path.join(fullDirectory, "code", "argos_basic.py"),'w') as codeFile:
        codeFile.write(argos_basic)


def parser_download_handler(arguments):

    if len(arguments.experimentDirectory) == 0:
        experimentDirectory = os.getcwd()

    elif len(arguments.experimentDirectory) == 1:
        experimentDirectory = os.path.abspath(arguments.experimentDirectory[0])
    else:
        raise ValueError(f"must get only one directory!. got {arguments.experimentDirectory}")



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
