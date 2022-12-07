import os
import json
from . import thingsboard as tb
from .experimentSetup import getExperimentSetup,FILE,WEB

DESIGN = 'design'
DEPLOY = 'deploy'


class experimentSetup:
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

    def setupExperiment(self, toDirectory : str =None ):
        """
            1. Create the computed devices in Thingsboard.
            2. Save the computed device files for NodeRed.

        :return:

            None
        """

        if toDirectory is None:
            toDirectory = os.getcwd()

        pathToDeviceFile = os.path.abspath(toDirectory)

        devicesList = self.experiment.getExperimentEntities()
        computedDevicesList = self._loadThingsboardDevices()
        self._setupDefaultAssets()

        with open(os.path.join(pathToDeviceFile,"devices.json"),"w") as outFile:
            outFile.write(json.dumps(devicesList, indent=4, sort_keys=True))

        with open(os.path.join(pathToDeviceFile,"computationalDevices.json"),"w") as outFile:
            outFile.write(json.dumps(computedDevicesList, indent=4, sort_keys=True))


    def packExperimentSetup(self, toDirectory : str):
        """
            Archive all the data of the experiment.

            Download the pictures from the


        Parameters
        ----------

        toDirectory : str
            The directory to pack the experiment to.


        Returns
        -------

        None
        """
        self.experiment.packExperimentSetup(toDirectory)

    def _setupDefaultAssets(self):
        """
            Loads default assets to TB:

            * Asset [Device type]_[window size]
                    contains all the devices of that window size.

            * Assets [Device type] that contains all the   [Device type]_[window size].

            * Assets


        :return:
        """
        computedDeviceList = self.buildThingsboardDevicesList()

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


    def buildThingsboardDevicesList(self):
        """
            Returns a list of the names of the computational entites out of the
            entites in the experiment and the computational windows.

        :return:
            A list of dict of the computational entites.
        """
        entites = self.experiment.getExperimentEntities()
        TBentitiesList = []
        for entityDict in entites:
            deviceName = entityDict['entityName']
            deviceType = entityDict['entityTypeName']
            windows = self.deviceComputationWindow.get(deviceType,None)

            if windows is not None:
                for window in windows:
                    windowDeviceName = self.getComputedDeviceName(deviceName,window)
                    windowDeviceType = deviceType

                    newdevice = dict(deviceName=windowDeviceName,
                                     window = window,
                                     parentDevice = deviceName,
                                     deviceType=windowDeviceType)
                    TBentitiesList.append(newdevice)
            else:
                newdevice = dict(deviceName=deviceName,
                                 window=None,
                                 parentDevice=None,
                                 deviceType=deviceType)
                TBentitiesList.append(newdevice)

        return TBentitiesList


    def _loadThingsboardDevices(self):
        """
            Create all the computed devices in the TB.

            Returns a list of computed devices with their TB credentials.


        :return:
               list of computed devices with their credentials.

        """
        TBDeviceList = self.buildThingsboardDevicesList()

        for TBDevice in TBDeviceList:
            dvceProxy = self.tbHome.deviceHome.createProxy(TBDevice['deviceName'],
                                                           TBDevice['deviceType'])

            TBDevice['credentials']=dvceProxy.getCredentials()

        return TBDeviceList

    def _loadToHera(self):
        """
            Creates the documents for the computational and raw data.

            the data is written in directory 'data'.

        :return:
        """
        try:
            from hera.datalayer import Measurements
            from hera.datalayer import datatypes

            for devicetype in self.experiment.entityType():

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

    def loadTrialDesign(self, trialSetName: str, trialName: str):
        self.loadTrial(trialSetName, trialName, 'design')

    def loadTrialDeploy(self, trialSetName: str, trialName: str):
        self.loadTrial(trialSetName, trialName, 'deploy')


    def loadTrial(self,trialSetName: str, trialName: str,state : str):

        for TBDevice in self.buildThingsboardDevicesList():
            print(f"Loading {TBDevice['deviceName']}, removing old property values")

            deviceType   = TBDevice['deviceType']
            deviceParent = TBDevice.get('parentDevice',None)

            # get the device data from the data manager
            if deviceParent is None:
                parentDevice = self.experiment.entityType[deviceType][TBDevice['deviceName']]
            else:
                parentDevice = self.experiment.entityType[deviceType][deviceParent]

            deviceProxy = self.tbHome.deviceHome.createProxy(entityName=TBDevice['deviceName'],
                                                             entityType=TBDevice['deviceType'])

            deviceProxy.delAttributes('locationName','SHARED_SCOPE')
            deviceProxy.delAttributes('longitude','SHARED_SCOPE')
            deviceProxy.delAttributes('latitude','SHARED_SCOPE')

            for propName in self.experiment.entityType[deviceType].properties.keys():
                deviceProxy.delAttributes(propName, 'SHARED_SCOPE')

            trialAttributes = parentDevice.trial(trialSetName,trialName,state)
            if len(trialAttributes) > 0:
                deviceProxy.setAttributes(trialAttributes,'SHARED_SCOPE')
            


    def dumpExperimentDevices(self,experimentName):
        """
            Writes the devices and the properties to a file.

        :return:
            None
        """
        devices = self.experiment.entities[['deviceTypeName', 'deviceName']]
        devicesJSON = [devices.loc[key].to_dict() for key in devices.index]


        with open(f"{experimentName}.json", 'w') as outputFile:
            outputFile.write(json.dumps(devicesJSON, indent=4, sort_keys=True))

