import os
import json
from . import thingsboard as tb
from .experimentSetup import getExperimentSetup,FILE,WEB

class ExperimentManager:
    """
        Manages the experiment.

        Provides interface to work with experiment setup (either file or web).

        contains the:

        - Interface to the experiment setup (from experimentSetup package)
        - Interface to the Thingsboard (TB).
        - Provides information on the shadow (computed) devices and their time window for operation.

        The structure of the configuration file:

        {

          "setupManager" : {
            "web" : {

            },
            "file" : {

            }
          },
          "thingsboard": {
            "login": {
              "username": "...",
              "password": "..."
            },
            "server": {
              "ip": "127.0.0.1",
              "port": "8080"
            }
          },
        "analysis": {
            <deviceName> : [list averaging windows (in sec)],
        }

        In addition, the definition of the experiment setup is given by:

        "web": {
            "experimentName" : ....
            "url": "...",
            "token": "..."
          },

        or

        "file": {
            "configurationFile": "...",
          },
    """


    _configuration = None
    _experiment = None
    _tbh = None
    _windowsDict = None

    @property
    def configuration(self):
        return self._configuration

    @property
    def deviceAveragingWindows(self):
        return self._configuration['analysis']

    @property
    def experimentName(self):
        return self._configuration['experimentName']
    
    @property
    def tbHome(self):
        if self._tbh is None:
            tb_config = self._configuration['thingsboard']
            self._tbh = tb.tbHome(tb_config)
        return self._tbh

    @property
    def experiment(self):
        return self._experiment


    def __init__(self, experimentConfiguration,datalayerType):
        """
            Initializes the experiment manager

        Parameters
        ----------
        experimentConfiguration : str, file or JSON
                The configuration file.

        datalayerType : str
            Either   MANAGER_FILE or MANAGER_WEB constants.
        """
        if datalayerType not in [FILE,WEB]:
            raise ValueError(f"datalayerType must be either FILE or WEB constant defined in ExperimentManager. Got {datalayerType}")

        if isinstance(experimentConfiguration,str):
            if os.path.exists(experimentConfiguration):
                with open(experimentConfiguration,'r')  as inputFile:
                    self._configuration = json.load(inputFile)
            else:
                try:
                    self._configuration = json.loads(experimentConfiguration)
                except json.JSONDecodeError:
                    raise ValueError("input must be a JSON file, JSON string or a JSON object")

        else:
            self._configuration = experimentConfiguration

        self._experiment = getExperimentSetup(datalayerType,**self._configuration['setupManager'][datalayerType])


    def setupExperiment(self):
        """
            1. Create the devices in Thingsboard.
            2. Get the credentials and add the to the device list.
            3. Create the Hera documents (if Hera exists).

        :return:
        """

        pathToDeviceFile = os.path.abspath(self.experimentConfigurationPath)

        devices = self.experiment.getExperimentDevices()
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

