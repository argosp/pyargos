import os
import json
from . import thingsboard as tb
from .experimentSetup import getExperimentSetup,FILE,WEB

class experimentManager:
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

    _datalayerType = None
    _autoRefresh = None

    @property
    def autoRefresh(self):
        return self._autoRefresh

    @autoRefresh.setter
    def autoRefresh(self, value):
        if value not in [True,False]:
            raise ValueError("autoRefresh must be boolean")
        self._autoRefresh = value


    @property
    def datalayerType(self):
        return self._datalayerType

    @property
    def experimentConfigurationPath(self):

        directory = self._configuration['experiment'].get("directory",None)

        if (directory is None) or directory =="none":
            directory = os.getcwd()

        return directory

    @property
    def configuration(self):
        return self._configuration

    @property
    def deviceAveragingWindows(self):
        return self._configuration['analysis']

    @property
    def experimentName(self):
        return self._configuration['experiment']['name']
    
    @property
    def tbHome(self):
        if self._tbh is None:
            tb_config = self._configuration['thingsboard']
            self._tbh = tb.tbHome(tb_config)
        return self._tbh

    @property
    def experiment(self):
        if self.autoRefresh:
            self.refresh()

        return self._experiment

    @property
    def deviceComputationWindow(self):
        return self._configuration['analysis']

    getComputedDeviceName = lambda self, deviceName,window: f'{deviceName}_{window}s'  # Creates the name of the device.

    def __init__(self, experimentConfiguration,datalayerType,autoRefresh = False):
        """
            Initializes the experiment manager

        Parameters
        ----------
        experimentConfiguration : str, file or JSON
                The configuration file.

        autoRefresh : bool
            If true, refresh the data every access to the experiment layer.
            Else, use the state when loaded.

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


        self._datalayerType = datalayerType
        self._autoRefresh = autoRefresh

        self.refresh()

    def refresh(self):
        self._experiment = getExperimentSetup(self.datalayerType, experimentName=self.experimentName,
                                              **self._configuration['setupManager'][self.datalayerType])

    def setupExperiment(self):
        """
            1. Create the computed devices in Thingsboard.
            2. Save the computed device files for NodeRed.

        :return:

            None
        """

        pathToDeviceFile = os.path.abspath(self.experimentConfigurationPath)

        devicesList = self.experiment.getExperimentDevices()
        computedDevicesList = self._loadComputedDevicesThingsboard()
        self._setupDefaultAssets()

        with open(os.path.join(pathToDeviceFile,"devices.json"),"w") as outFile:
            outFile.write(json.dumps(devicesList, indent=4, sort_keys=True))

        with open(os.path.join(pathToDeviceFile,"computationalDevices.json"),"w") as outFile:
            outFile.write(json.dumps(computedDevicesList, indent=4, sort_keys=True))



    def _setupDefaultAssets(self):
        """
            Loads default assets to TB:

            * Asset [Device type]_[window size]
                    contains all the devices of that window size.

            * Assets [Device type] that contains all the   [Device type]_[window size].

            * Assets


        :return:
        """
        computedDeviceList = self.getComputationalDeviceList()

        for computedDevice in computedDeviceList:

            window = computedDevice['window']

            # Device asset proxy
            deviceTypeAssetProxy =  self.tbHome.assetHome.createProxy(entityName=computedDevice['deviceType'],
                                                           entityType="computedDevices")

            # Get the asset proxy
            windowAssetProxy = self.tbHome.assetHome.createProxy(entityName=f"Window {window}s",
                                                           entityType="windowComputedDevices")

            # Get the device proxy.
            deviceProxy = self.tbHome.deviceHome.createProxy(entityName=computedDevice['deviceName'],
                                                             entityType=computedDevice['deviceType'])

            windowAssetProxy.addRelation(deviceProxy)
            deviceTypeAssetProxy.addRelation(windowAssetProxy)


    def getComputationalDeviceList(self):
        """
            Returns a list of the names of the computational devices out of the
            devices in the experiment and the computational windows.

        :return:
            A list of dict of the computational devices.
        """
        devices = self.experiment.getExperimentDevices()
        computationDeviceList = []
        for deviceDict in devices:
            deviceName = deviceDict['deviceName']
            deviceType = deviceDict['deviceTypeName']
            windows = self.deviceComputationWindow[deviceType]

            for window in windows:
                windowDeviceName = self.getComputedDeviceName(deviceName,window)
                windowDeviceType = deviceType

                newdevice = dict(deviceName=windowDeviceName,
                                 window = window,
                                 parentDevice = deviceName,
                                 deviceType=windowDeviceType) # credentials=dvceProxy.getCredentials())
                computationDeviceList.append(newdevice)

        return computationDeviceList


    def _loadComputedDevicesThingsboard(self):
        """
            Create all the computed devices in the TB.

            Returns a list of computed devices with their TB credentials.


        :return:
               list of computed devices with their credentials.

        """
        computedDeviceList = self.getComputationalDeviceList()

        for computationalDevice in computedDeviceList:
            dvceProxy = self.tbHome.deviceHome.createProxy(computationalDevice['deviceName'],
                                                           computationalDevice['deviceType'])

            computationalDevice['credentials']=dvceProxy.getCredentials()

        return computedDeviceList

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

    def loadTrialDesignToTBF(self, trialSetName: str, trialName: str):
        self.loadTrial(trialSetName, trialName, 'design')

    def loadTrialDeployToTBF(self, trialSetName: str, trialName: str):
        self.loadTrial(trialSetName, trialName, 'deploy')





    def loadTrial(self,trialSetName: str, trialName: str,state : str):

        for computedDevice in self.getComputationalDeviceList():

            deviceType   = computedDevice['deviceType']
            deviceParent = computedDevice['parentDevice']

            # get the device data from the data manager
            parentDevice = self.experiment.deviceType[deviceType][deviceParent]

            deviceProxy = self.tbHome.deviceHome.createProxy(entityName=computedDevice['deviceName'],
                                                             entityType=computedDevice['deviceType'])

            trialAttributes = parentDevice.trial(trialSetName,trialName,state)

            deviceProxy.setAttributes(trialAttributes,'SHARED_SCOPE')
            












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

