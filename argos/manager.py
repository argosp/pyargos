import os
import json
from . import thingsboard as tb
from .datalayer.argosWebDatalayer import GQLDataLayerFactory

from typing import Union

class ExperimentManager:

    _expConf = None
    _experiment = None
    _tbh = None
    _windowsDict = None

    @property
    def experimentConfigurationPath(self):
        return self._expConf['experimentConfigurationPath']

    @property
    def experimentName(self):
        return self._expConf['experimentName']
    
    @property
    def tbHome(self):

        if self._tbh is None:
            tb_config = self._expConf['thingsboard']
            self._tbh = tb.tbHome(tb_config)


        return self._tbh

    @property
    def experiment(self):
        return self._experiment


    def __init__(self, datalayerCLS, expConf):
        """

        :param datalayer: Datalayer class
                Either argosWeb or JSON datalayer.
        :param expConf : str, file or JSON
                The configuration file.
        """

        if type(expConf) is str:
            with open(expConf, 'r') as myFile:
                expConf = json.load(myFile)
        self._expConf = expConf

        gql_config = expConf['graphql']
        self._experiment = GQLDataLayerFactory(experimentConfiguration=expConf).experiment

        self._windowsDict = expConf['analysis']

    def setupExperiment(self):
        """
            1. Create the devices in Thingsboard.
            2. Get the credentials and add the to the device list.
            3. Create the Hera documents (if Hera exists).

        :return:
        """

        pathToDeviceFile = os.path.abspath(self.experimentConfigurationPath)

        devices = self._experiment.getExperimentDevices()
        deviceList,computationDeviceList = self._loadToThingsboard(devices)

        self._loadToHera()

        with open(os.path.join(pathToDeviceFile,"devices.json"),"w") as outFile:
            outFile.write(json.dumps(deviceList, indent=4, sort_keys=True))

        with open(os.path.join(pathToDeviceFile,"computationalDevices.json"),"w") as outFile:
            outFile.write(json.dumps(computationDeviceList, indent=4, sort_keys=True))

        return deviceList

    def _loadToThingsboard(self,devices : list):
        """
            Create all the computed devices in the TB

        :param deviceDict: list
                The list of  {'deviceName': <device Name>, 'deviceTypeName': <device Type>}

        :return: tuple
                * list of devices with the credentials, adds the windowed devices as well.
                * list of computed devices.

        """
        deviceList = []
        computationDeviceList = []
        for deviceDict in devices:
            deviceName = deviceDict['deviceName']
            deviceType = deviceDict['deviceTypeName']
            windows = self._windowsDict[deviceType]
            #dvceProxy = self.tbHome.deviceHome.createProxy(deviceName, deviceType)
            #deviceDict['credentials'] = dvceProxy.getCredentials()

            deviceList.append(dict(deviceDict))
            for window in windows:
                windowDeviceName = f'{deviceName}_{window}s'
                windowDeviceType = f'calculated_{deviceType}'
                dvceProxy = self.tbHome.deviceHome.createProxy(windowDeviceName, windowDeviceType)
                newdevice = dict(deviceName=windowDeviceName,deviceTypeName=windowDeviceType,credentials=dvceProxy.getCredentials())

                computationDeviceList.append(newdevice)

        return deviceList,computationDeviceList

    def _loadToHera(self):
        """
            Creates the documents for the computational and raw data.

            the data is written in directory 'data'.

        :return:
        """
        try:
            from hera.datalayer import Measurements
            from hera.datalayer import datatypes

            for devicetype in self.experiment.deviceType():
                windowsList = self._windowsDict[devicetype]

                dataPath = os.path.join(os.path.abspath("."),"data")

                # rawData
                docList = Measurements.getDocuments(projectName=self.experimentName,
                                                    type='rawData',
                                                    deviceType=devicetype)


                if len(docList)==0:

                    Measurements.addDocument(projectName=self.experimentName,
                                              dataFormat=datatypes.PARQUET,
                                              type='rawData',
                                              resource=os.path.join(dataPath, f"{devicetype}.parquet"),
                                              desc=dict(experimentName=self.experimentName,
                                                        deviceType=devicetype)

                                              )
                # --------------------------
                # For now we don't need the computations.
                # we can calculate them simply from the real data.
                #
                #
                # for window in windowsList:
                #     docList = Measurements.getDocuments(projectName=self.experimentName,
                #                                         type='rawData',
                #                                         deviceType=devicetype,
                #                                         window=window)
                #
                #     if len(docList)==0:
                #         Measurements.addDocument(projectName=self.experimentName,
                #                                  dataFormat=datatypes.PARQUET,
                #                                  type='computationalData',
                #                                  resource=os.path.join(dataPath, f"{devicetype}_{window}.parquet"),
                #                                  desc=dict(experimentName=self.experimentName,
                #                                            deviceType=devicetype,
                #                                            window=window)
                #
                #                                  )




        except ImportError:
            print("Hera is not found. Cannot create the documents.")


    def createTrialDevicesThingsboard(self, trialSetName: str, trialName: str, trialType: str = 'deploy'):

        devices = self.glDL.getThingsboardTrialLoadConf(self.experimentName, trialSetName, trialName, trialType)
        for deviceDict in devices:
            windows = self._windowsDict[deviceDict['deviceTypeName']]
            deviceProxy = self.tbHome.deviceHome.createProxy(deviceDict['deviceName'])
            for attributeKey, attributeValue in deviceDict['attributes'].items():
                deviceProxy.delAttributes(attributeKey)
                deviceProxy.setAttributes(deviceDict['attributes'])
                for window in windows:
                    windowDeviceName = f'{deviceDict["deviceName"]}_{window}s'
                    windowDeviceProxy = self.tbHome.deviceHome.createProxy(windowDeviceName)
                    windowDeviceProxy.delAttributes(attributeKey)
                    windowDeviceProxy.setAttributes(deviceDict['attributes'])

    def loadTrialDesignToTBF(self, trialSetName: str, trialName: str):
        self.loadTrial(trialSetName, trialName, 'design')

    def loadTrialDeployToTBF(self, trialSetName: str, trialName: str):
        self.loadTrial(trialSetName, trialName, 'deploy')


    def dumpExperimentDevices(self,experimentName):
        """
            Writes the devices and the properties to a file.

        :return:
            None
        """
        devices = self.experiment.devices[['deviceTypeName', 'deviceName']]
        devicesJSON = [devices.loc[key].to_dict() for key in devices.index]


        with open(f"{experimentName}.json", 'w') as outputFile:
            outputFile.write(json.dumps(devicesJSON, indent=4, sort_keys=True))

