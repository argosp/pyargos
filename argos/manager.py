import os
import json
from tb_rest_client.rest_client_ce import *
from .experimentSetup.dataObjectsFactory import fileExperimentFactory
from .utils.jsonutils import loadJSON
from .utils.logging import get_classMethod_logger

DESIGN = 'design'
DEPLOY = 'deploy'


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

    @property
    def restClient(self):
        """
            Returns the rest client.
             Reads the configuration from the

        Returns
        -------

        """
        confFile = os.path.join(self.experimentDirectory, "runtimeExperimentData", "Datasources_Configurations.json")
        configuration = loadJSON(confFile)
        tbConfiguration = configuration['Thingsboard']

        rest_client = RestClientCE(base_url=tbConfiguration['url'])
        rest_client.login(username=tbConfiguration['username'], password=tbConfiguration['password'])
        return rest_client

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

    @property
    def experiment(self):
        """
            Returns the experiment factory from the ZIP file.
        Returns
        -------

        """
        return fileExperimentFactory(self.experimentDirectory).getExperiment()

    def loadThingsboardDevices(self):
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
                if len(restClient.get_tenant_device_infos(page_size=100, page=0, text_search=deviceData['name']).data) == 0:
                    device = Device(name=deviceData['name'], device_profile_id=device_profile.id)
                    device = restClient.save_device(device)
                    logger.info(" Device was created:\n%r\n", device)
                else:
                    logger.debug(f"Device {deviceData['name']} exists... skipping")

    def loadTrialDesign(self, trialSetName: str, trialName: str):
        self.loadTrial(trialSetName, trialName, 'design')

    def loadTrialDeploy(self, trialSetName: str, trialName: str):
        self.loadTrial(trialSetName, trialName, 'deploy')


    def loadTrial(self,trialSetName: str, trialName: str,state : str):
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

        for deviceName, deviceData in experiment.trialSet[trialSetName][trialName].entities(state).items():
            logger.info(f"Setting up the attributes for device {deviceName}")

            logger.debug("Remove the properties")
            device = restClient.get_tenant_devices(page_size=1000, page=0, text_search=deviceName).data[0]
            for scopeName in [SERVER_SCOPE,SHARED_SCOPE,CLIENT_SCOPE]:
                keysList = restClient.get_attributes(device.id,SERVER_SCOPE)
                restClient.delete_device_attributes(device.id, scope=scopeName, keys=keysList)

            restClient.save_device_attributes(device.id, "SERVER_SCOPE",deviceData)











