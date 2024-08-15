import os
import json
import pandas
from .utils.jsonutils import loadJSON
import logging
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaConsumer,KafkaProducer
import threading
from .kafka.consumer import consume_topic,consume_topic_server
from .manager import experimentManager

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
    expDict = dict(experimentName=arguments.experimentName,kafka=dict(bootstrap_servers=["127.0.0.1:9092"]))
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

def nodered_createDeviceMap(arguments):
    logger = logging.getLogger("argos.bin.nodered_createDeviceList")
    logger.info("--------- Start ---------")

    expr = fileExperimentFactory().getExperiment()
    entDict = []
    logger.debug("Iterating over devices: ")
    for endID,ent in expr.entitiesTable.iterrows():
        logger.debug(f"\t{ent['name']} -> {ent['entityType']} ")
        entDict.append( (ent['name'],ent['entityType'] ) )

    deviceMapFileName = os.path.join(os.getcwd(),"runtimeExperimentData","deviceMap.json")
    logger.info(f"Writing file {deviceMapFileName}")
    with open(deviceMapFileName,"w") as deviceMap:
        json.dump(dict(entDict),deviceMap,indent=4)

def kafka_createTopics(args):
    logger = logging.getLogger("argos.bin.kafka_createTopics")
    logger.info("--------- Start ---------")

    if not os.path.isdir(os.path.join(os.getcwd(),"runtimeExperimentData")):
        err = f"{os.getcwd()} is not an experiment directory"
        logger.error(err)
        raise ValueError(err)


    confFile = os.path.join(os.getcwd(),"runtimeExperimentData","Datasources_Configurations.json")
    if not os.path.isfile(confFile):
        err = f"{confFile} does not exist!"
        logger.error(err)
        raise ValueError(err)

    logger.execution(f"Loading the configuration file {confFile}")
    configuration = loadJSON(os.path.join(os.getcwd(),"runtimeExperimentData","Datasources_Configurations.json"))
    bootstrap_servers = configuration['kafka']['bootstrap_servers']
    logger.info("Checking if all the device topics exist, if not - create them")
    # Create a Kafka admin client
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)

    exprerimentDescription = fileExperimentFactory(os.getcwd()).getExperiment()

    devices = [x for x in exprerimentDescription.entityTypeTable.entityType.unique()]+["kafkaConsumerServer"]
    deviceExist = dict([(x['topic'],x['error_code']) for x in  admin_client.describe_topics(devices)])

    newTopicList =[]
    for deviceName,deviceExists in deviceExist.items():
        exists = True if deviceExists==0 else False
        logger.info(f"device type {deviceName} topic {'exists' if exists else 'does NOT exist... creating'}")
        if not exists:
            newTopicList.append(NewTopic(name=deviceName, num_partitions=1, replication_factor=1))

    admin_client.create_topics(new_topics=newTopicList)


def kafka_runConsumerTopic(args):
    logger = logging.getLogger("argos.bin.kafka_runConsumerTopic")
    logger.info("--------- Start ---------")
    consume_topic(args.topic, os.path.join(os.getcwd(), "data"))

def kafka_runConsumers(args):
    logger = logging.getLogger("argos.bin.kafka_runConsumers")
    logger.info("--------- Start ---------")

    if not os.path.isdir(os.path.join(os.getcwd(),"runtimeExperimentData")):
        err = f"{os.getcwd()} is not an experiment directory"
        logger.error(err)
        raise ValueError(err)


    confFile = os.path.join(os.getcwd(),"runtimeExperimentData","Datasources_Configurations.json")
    if not os.path.isfile(confFile):
        err = f"{confFile} does not exist!"
        logger.error(err)
        raise ValueError(err)

    logger.execution(f"Loading the configuration file {confFile}")
    configuration = loadJSON(os.path.join(os.getcwd(),"runtimeExperimentData","Datasources_Configurations.json"))
    bootstrap_servers = configuration['kafka']['bootstrap_servers']
    logger.info("Checking if all the device topics exist, if not - create them")
    kafka_createTopics(args)

    logger.execution("Create the consumers")
    exprerimentDescription = fileExperimentFactory(os.getcwd()).getExperiment()
    devices = [x for x in exprerimentDescription.entityTypeTable.entityType.unique()]

    threadList = []
    for device in devices:
        logger.info(f"Creating thread for {device}")
        threadList.append(threading.Thread(target=consume_topic, args=(device,os.path.join(os.getcwd(),"data"))))

    logger.info(f"executing threads")
    for thread in threadList:
        thread.start()

    logger.info(f"Waiting for threads")
    for thread in threadList:
        thread.join()

    logger.info("Finished consuming the data")

def kafka_runConsumersServer(args):
    logger = logging.getLogger("argos.bin.kafka_runConsumersServer")
    logger.info("--------- Start ---------")

    if not os.path.isdir(os.path.join(os.getcwd(),"runtimeExperimentData")):
        err = f"{os.getcwd()} is not an experiment directory"
        logger.error(err)
        raise ValueError(err)


    confFile = os.path.join(os.getcwd(),"runtimeExperimentData","Datasources_Configurations.json")
    if not os.path.isfile(confFile):
        err = f"{confFile} does not exist!"
        logger.error(err)
        raise ValueError(err)

    logger.info("Opening a listener on topic 'kafkaConsumerServer'. Send a message to intiate an update")
    consumer = KafkaConsumer(
        "kafkaConsumerServer",
        bootstrap_servers='127.0.0.1:9092',
        group_id='1',
        auto_offset_reset='earliest',
        max_poll_records=12000
        # Add more consumer configuration options as needed
    )

    delayInSeconds = pandas.to_timedelta(args.delay).value/1e9
    logger.info(f"Starting a server with polling every {args.delay} ({delayInSeconds} seconds)")

    logger.execution("Create the consumers")
    exprerimentDescription = fileExperimentFactory(os.getcwd()).getExperiment()
    devices = [x for x in exprerimentDescription.entityTypeTable.entityType.unique()]

    threadList = []
    for device in devices:
        logger.info(f"Creating thread for {device}")
        threadList.append(threading.Thread(target=consume_topic_server, args=(device, os.path.join(os.getcwd(), "data"),delayInSeconds)))

    logger.info(f"executing threads")
    for thread in threadList:
        thread.start()

    logger.info(f"Waiting for threads")
    for thread in threadList:
        thread.join()

    # while True:
    #     logger.execution(f"Loading the configuration file {confFile}")
    #     configuration = loadJSON(os.path.join(os.getcwd(),"runtimeExperimentData","Datasources_Configurations.json"))
    #     bootstrap_servers = configuration['kafka']['bootstrap_servers']
    #     logger.info("Checking if all the device topics exist, if not - create them")
    #     kafka_createTopics(args)
    #
    #     logger.info(f"executing threads")
    #     for thread in threadList:
    #         thread.start()
    #
    #     logger.info(f"Waiting for threads")
    #     for thread in threadList:
    #         thread.join()
    #
    #     logger.info(f"Waiting for {args.delay} ({delayInSeconds} seconds), check every 5s")
    #     for i in range(int(delayInSeconds/5)+1):
    #         logger.info(f"Waiting for {i*5} sec out of {delayInSeconds}")
    #         activation = consumer.poll()
    #         if numpy.sum([len(x) for x in activation.values()]) > 0:
    #             logger.info("Got reuest for consume")
    #             break
    #         time.sleep(5)


def Thingsboard_loadTrial(args):
    directory = os.getcwd() if args.directory is None else args.directory

    manager = experimentManager(directory)
    manager.loadTrialDesignToThingsboard(args.trialName,"design")

def Thingsboard_clean_devices(args):

    directory = os.getcwd() if args.directory is None else args.directory

    manager = experimentManager(directory)
    manager.clearDevicesFromThingsboard()



# def parser_download_handler(arguments):
#
#     if len(arguments.experimentDirectory) == 0:
#         experimentDirectory = os.getcwd()
#
#     elif len(arguments.experimentDirectory) == 1:
#         experimentDirectory = os.path.abspath(arguments.experimentDirectory[0])
#     else:
#         raise ValueError(f"must get only one directory!. got {arguments.experimentDirectory}")
#
#
#
#     configurtionFileName = os.path.join(experimentDirectory,"runtimeExperimentData","Datasources_Configurations.json")
#
#     with open(configurtionFileName) as jsonConfFile:
#         configurationFile = json.load(jsonConfFile)
#
#     experimentName = configurationFile['experimentName']
#     destDir = os.path.join(experimentDirectory,"runtimeExperimentData",experimentName)
#
#     mng = experimentSetup(configurationFile,argos.WEB)
#     print(f"Downloading experiment {experimentName} into directory {destDir}")
#     mng.packExperimentSetup(destDir)


def Thingsboard_register(argumets):
    """
        Gets the rest toke and saves it in the Datasources_Configuration.json

    Parameters
    ----------
    argumets :
        The directory of the experiment.

    Returns
    -------

    """

def Thingsboard_setupExperiment(arguments):

    experimentDirectory = arguments.directory

    configurtionFileName = os.path.join(experimentDirectory,"runtimeExperimentData","Datasources_Configurations.json")
    configurationFile = loadJSON(configurtionFileName)

    experimentName = configurationFile['experimentName']
    destDir = os.path.join(experimentDirectory,"runtimeExperimentData")

    mng = fileExperimentFactory(os.getcwd()).getExperiment()
    print(f"Uploading experiment {experimentName} to Thingsboard")
    print(f"Writing configuration files")
    mng.setupExperiment(destDir)
    print("...Done")

# #
# def Thingsboard_GetImageMapping(args):
#
#
#     if len(args.args) == 1:
#         experimentDirectory = os.getcwd()
#         inputFormat = args.args[0].lower()
#
#     elif len(args.experimentDirectory) == 2:
#         experimentDirectory = os.path.abspath(args.experimentDirectory[0])
#         inputFormat = args.args[1].tolower()
#     else:
#         raise ValueError(f"Must get . got {args.experimentDirectory}")
#
#     if inputFormat not in [argos.WEB, argos.FILE]:
#         raise ValueError(f"Please specify correct input format: {argos.WEB} or {argos.FILE}. Got {inputFormat}")
#
#
#     configurtionFileName = os.path.join(experimentDirectory, "runtimeExperimentData",
#                                         "Datasources_Configurations.json")
#
#     with open(configurtionFileName) as jsonConfFile:
#         configurationFile = json.load(jsonConfFile)
#
#     mng = experimentSetup(configurationFile, inputFormat)
#
#     for imageName,imageData in mng.experiment.imageMap.items():
#         print(f"----------------- {imageName} --------------------")
#         print(mng.experiment.getImageJSMappingFunction(imageName))

#
# def parser_loadTrial_handler(args):
#
#     if len(args.args) == 1:
#         experimentDirectory = os.getcwd()
#         inputFormat = args.args[0].lower()
#
#     elif len(args.experimentDirectory) == 2:
#         experimentDirectory = os.path.abspath(args.experimentDirectory[0])
#         inputFormat = args.args[1].tolower()
#     else:
#         raise ValueError(f"Must get . got {args.experimentDirectory}")
#
#     if inputFormat not in [argos.WEB, argos.FILE]:
#         raise ValueError(f"Please specify correct input format: {argos.WEB} or {argos.FILE}. Got {inputFormat}")
#
#
#     configurtionFileName = os.path.join(experimentDirectory, "runtimeExperimentData",
#                                         "Datasources_Configurations.json")
#
#     with open(configurtionFileName) as jsonConfFile:
#         configurationFile = json.load(jsonConfFile)
#
#     trialSetName,trialName = args.trial
#     state = args.state.lower()
#
#     if state not in ['design','deploy']:
#         raise ValueError(f"The state must be design or deploy. Got {state}")
#
#     mng = experimentSetup(configurationFile, inputFormat)
#     mng.loadTrial(trialSetName,trialName,state)

