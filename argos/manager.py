import json
from . import thingsboard as tb
from .datalayer.argosWebDatalayer import GQLDataLayerFactory

from typing import Union

class ExperimentManager:

    _expConf = None
    _experimentDatalayer = None
    _tbh = None
    _windowsDict = None

    @property
    def experimentName(self):
        return self._expConf['name']
    
    @property
    def tbHome(self):

        if self._tbh is None:
            tb_config = self._expConf['thingsboard']
            self._tbh = tb.tbHome(tb_config)


        return self._tbh

    @property
    def datalayer(self):
        return self._experimentDatalayer

    @property
    def experiment(self):
        return self.experiment.getExperimentByName(self.experimentName)

    def __init__(self, expConf: Union[str, dict]):
        """

        :param expConf: The experiment configuration
        """

        if type(expConf) is str:
            with open(expConf, 'r') as myFile:
                expConf = json.load(myFile)
        self._expConf = expConf

        gql_config = expConf['graphql']
        self._experimentDatalayer = GQLDataLayerFactory(url=gql_config['url'], token=gql_config['token'])


        self._windowsDict = {deviceType: list(self._expConf['kafka']['consumers'][deviceType]['processes'].keys()) for deviceType in self._expConf['kafka']['consumers'].keys()}

    def setup(self):
        devices = self._experimentDatalayer.getExperimentDevices(experimentName=self.experimentName)
        for deviceDict in devices:
            deviceName = deviceDict['deviceName']
            deviceType = deviceDict['deviceTypeName']
            windows = self._windowsDict[deviceType]
            self.tbHome.deviceHome.createProxy(deviceName, deviceType)
            for window in windows:
                windowDeviceName = f'{deviceName}_{window}s'
                windowDeviceType = f'calculated_{deviceType}'
                self.tbHome.deviceHome.createProxy(windowDeviceName, windowDeviceType)

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

