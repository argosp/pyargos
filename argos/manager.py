import os
import json
try:
    from tb_rest_client.rest_client_ce import *
except ImportError:
    print("Thingsboard interface not installed. Use pip install tb_rest_client.")
from .experimentSetup.dataObjectsFactory import fileExperimentFactory
from .utils.jsonutils import loadJSON
from .utils.logging import get_classMethod_logger



SERVER_SCOPE = "SERVER_SCOPE"
SHARED_SCOPE = "SHARED_SCOPE"
CLIENT_SCOPE = "CLIENT_SCOPE"

class experimentManager:
    """
        Manages the experiment.

        Provides interface to work with experiment setup (either file or web).

        contains the:

        - Interface to the Thingsboard (TB).
        - Provides information on the shadow (computed) devices and their time window for operation.

        The structure of the configuration file:


    """
    experimentDirectory = None

    configuration = None

    def __init__(self, experimentDirectory):
        """
            Initializes the experiment manager

        Parameters
        ----------
        directory : str,
                The directory to the exeriment.
                The path to the zipfile is <directory>/runtimeExperimentData/Datasources_Configurations.json

        autoRefresh : bool
            If true, refresh the data every access to the experiment layer.
            Else, use the state when loaded.

        """
        self.experimentDirectory = experimentDirectory
        self.loadConfigutation()

    def loadConfigutation(self):
        confFile = os.path.join(self.experimentDirectory, "runtimeExperimentData", "Datasources_Configurations.json")
        self.configuration = loadJSON(confFile)


    @property
    def TBConfiguration(self):
        return self.configuration['Thingsboard']

    @property
    def restClient(self):
        """
            Returns the rest client.
             Reads the configuration from the

        Returns
        -------

        """
        tbConfiguration = self.TBConfiguration

        rest_client = RestClientCE(base_url=tbConfiguration['restURL'])
        rest_client.login(username=tbConfiguration['username'], password=tbConfiguration['password'])
        return rest_client

    @property
    def experiment(self):
        """
            Returns the experiment factory from the ZIP file.
        Returns
        -------

        """
        return fileExperimentFactory(self.experimentDirectory).getExperiment()

    def clearDevicesFromThingsboard(self):
        """
            Removes all the devices from Thingsboard.
        Returns
        -------

        """
        logger = get_classMethod_logger(self,"loadThingsboardDevices")

        restClient = self.restClient
        logger.info(f"Getting the devices from the Thingsboard server")
        deviceList = restClient.get_tenant_device_infos(page_size=1000, page=0)

        for device in deviceList.data:
            logger.info(f"Remove {device.name}")
            restClient.delete_device(device.id)

    def getDeviceMap(self,deviceType=None):
        """
            Returns a map of deviceName -> { 'credential' : .. , 'type' : ... }
        Parameters
        ----------
        deviceType : str
            Query one device type. Return all if None.

        Returns
        -------

        """
        logger = get_classMethod_logger(self, "loadThingsboardDevices")
        restClient = self.restClient
        deviceList = restClient.get_tenant_device_infos(page_size=1000, page=0)

        ret = dict()
        for device in deviceList.data:
            logger.debug(f"Getting info for device {device.name} of type {device.type}")
            if device.type != deviceType:
                logger.debug(f"... it is {device.type}, filtering out")
                continue
            credential = restClient.get_device_credentials_by_device_id(device.id).credentials_id
            ret[device.name] = dict(credential=credential,type=device.type)

        return ret

    def loadDevicesToThingsboard(self):
        """
            Create all the computed devices in the TB.

            Returns a list of computed devices with their TB credentials.


        :return:
               list of computed devices with their credentials.

        """
        logger = get_classMethod_logger(self,"loadThingsboardDevices")
        experiment = self.experiment
        restClient = self.restClient

        logger.info("Loading the devices in the experiment")
        existingProfiles = dict([(x.name,x.id.id) for x in restClient.get_device_profile_names(active_only=False)])
        logger.info(f"The existing profiles are : \n {existingProfiles}")
        for deviceNameType,deviceList in experiment.entitiesTable.groupby("entityType"):
            logger.debug(f"Checking if the device profile exists {deviceNameType}")
            if deviceNameType not in existingProfiles:
                logger.debug(f"Adding the device profile {deviceNameType}")
                device_profile = DeviceProfile(name=deviceNameType,
                                               type="DEFAULT",
                                               transport_type="DEFAULT",
                                               profile_data=DeviceProfileData(configuration={"type": "DEFAULT"},
                                                                              transport_configuration={"type": "DEFAULT"}))
                device_profile = restClient.save_device_profile(device_profile)
                existingProfiles[deviceNameType] = device_profile.id
            else:
                logger.debug(f"Exists, getting it from the server")
                device_profile = restClient.get_device_profile_info_by_id(existingProfiles[deviceNameType])

            for deviceID,deviceData in deviceList.iterrows():
                logger.debug(f"Device name: {deviceData['name']}")
                if len(restClient.get_tenant_device_infos(page_size=1000, page=0, text_search=deviceData['name']).data) == 0:
                    device = Device(name=deviceData['name'], device_profile_id=device_profile.id)
                    device = restClient.save_device(device)
                    logger.info(" Device was created:\n%r\n", device)
                else:
                    logger.debug(f"Device {deviceData['name']} exists... skipping")

    def loadTrialDesignToThingsboard(self, trialSetName: str, trialName: str):
        self.loadTrialToThingsboard(trialSetName, trialName)

    def loadTrialDeployToThingsboard(self, trialSetName: str, trialName: str):
        self.loadTrialToThingsboard(trialSetName, trialName)


    def loadTrialToThingsboard(self, trialSetName: str, trialName: str):
        """
            Loading the data of the trial to things board.
        Parameters
        ----------
        trialSetName
        trialName
        state

        Returns
        -------

        """
        logger = get_classMethod_logger(self,"loadThingsboardDevices")
        experiment = self.experiment
        restClient = self.restClient

        for deviceName, deviceData in experiment.trialSet[trialSetName][trialName].entitiesTable().items():
            logger.info(f"Setting up the attributes for device {deviceName}")

            logger.debug("Remove the properties")
            device = restClient.get_tenant_devices(page_size=1000, page=0, text_search=deviceName).data[0]
            for scopeName in [SERVER_SCOPE,SHARED_SCOPE,CLIENT_SCOPE]:
                keysList = restClient.get_attributes(device.id,SERVER_SCOPE)
                restClient.delete_device_attributes(device.id, scope=scopeName, keys=keysList)

            restClient.save_device_attributes(device.id, "SERVER_SCOPE",deviceData)











