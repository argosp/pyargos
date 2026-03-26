"""
Experiment manager with ThingsBoard integration.

This module provides the ``experimentManager`` class, which acts as the
unified interface between experiment configuration (loaded from files)
and the ThingsBoard IoT platform for device management and trial deployment.
"""

import os
import json
try:
    from tb_rest_client.rest_client_ce import *
except ImportError:
    print("Thingsboard interface not installed. Use pip install tb_rest_client.")
from .experimentSetup.dataObjectsFactory import fileExperimentFactory
from .utils.jsonutils import loadJSON
from .utils.logging import get_classMethod_logger


#: ThingsBoard attribute scope: server-side attributes.
SERVER_SCOPE = "SERVER_SCOPE"
#: ThingsBoard attribute scope: shared between server and device.
SHARED_SCOPE = "SHARED_SCOPE"
#: ThingsBoard attribute scope: device-side attributes.
CLIENT_SCOPE = "CLIENT_SCOPE"

class experimentManager:
    """
    Unified interface for managing experiments and ThingsBoard devices.

    Provides methods to load experiment definitions from local files,
    create devices and profiles on ThingsBoard, upload trial attributes,
    and query device credentials.

    Parameters
    ----------
    experimentDirectory : str
        Path to the experiment root directory. Must contain
        ``runtimeExperimentData/Datasources_Configurations.json``.

    Examples
    --------
    >>> from argos.manager import experimentManager
    >>> manager = experimentManager("/path/to/experiment")
    >>> manager.loadDevicesToThingsboard()
    >>> manager.loadTrialDesignToThingsboard("design", "myTrial")
    """
    experimentDirectory = None

    configuration = None

    def __init__(self, experimentDirectory):
        """
        Initialize the experiment manager.

        Loads the datasources configuration from the experiment directory.

        Parameters
        ----------
        experimentDirectory : str
            Path to the experiment root directory. The configuration file
            is expected at ``<dir>/runtimeExperimentData/Datasources_Configurations.json``.
        """
        self.experimentDirectory = experimentDirectory
        self.loadConfigutation()

    def loadConfigutation(self):
        """
        Reload the datasources configuration from disk.

        Reads ``Datasources_Configurations.json`` from the experiment's
        ``runtimeExperimentData/`` directory and stores it in
        ``self.configuration``.
        """
        confFile = os.path.join(self.experimentDirectory, "runtimeExperimentData", "Datasources_Configurations.json")
        self.configuration = loadJSON(confFile)


    @property
    def TBConfiguration(self):
        """
        The ThingsBoard section of the datasources configuration.

        Returns
        -------
        dict
            A dictionary with ``restURL``, ``username``, and ``password`` keys.
        """
        return self.configuration['Thingsboard']

    @property
    def restClient(self):
        """
        Create and return an authenticated ThingsBoard REST client.

        A new client is created and authenticated on each access.

        Returns
        -------
        RestClientCE
            An authenticated ThingsBoard Community Edition REST client.

        Raises
        ------
        NameError
            If ``tb_rest_client`` is not installed.
        """
        tbConfiguration = self.TBConfiguration

        rest_client = RestClientCE(base_url=tbConfiguration['restURL'])
        rest_client.login(username=tbConfiguration['username'], password=tbConfiguration['password'])
        return rest_client

    @property
    def experiment(self):
        """
        Load and return the experiment object from local files.

        Uses ``fileExperimentFactory`` to load the experiment from the
        experiment directory on each access.

        Returns
        -------
        Experiment
            The loaded experiment object.
        """
        return fileExperimentFactory(self.experimentDirectory).getExperiment()

    def clearDevicesFromThingsboard(self):
        """
        Remove all tenant devices from the ThingsBoard server.

        .. warning::
            This removes **all** devices belonging to the tenant, not just
            those in the current experiment. Use with caution.
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
        Get a map of device names to their credentials and types.

        Parameters
        ----------
        deviceType : str, optional
            Filter by device type name. If None, returns all devices.

        Returns
        -------
        dict[str, dict]
            A dictionary mapping device names to dicts with ``credential``
            and ``type`` keys. Example::

                {"Sensor_01": {"credential": "abc123", "type": "Sensor"}}
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
        Create all experiment entities as devices on ThingsBoard.

        For each entity type in the experiment:

        1. Checks if a device profile exists on ThingsBoard; creates one if not.
        2. For each entity, checks if the device already exists; creates it if not.

        Existing devices are skipped (not updated).
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
        """
        Upload a trial design to ThingsBoard.

        Delegates to :meth:`loadTrialToThingsboard`.

        Parameters
        ----------
        trialSetName : str
            The trial set name (e.g., ``"design"``).
        trialName : str
            The trial name.
        """
        self.loadTrialToThingsboard(trialSetName, trialName)

    def loadTrialDeployToThingsboard(self, trialSetName: str, trialName: str):
        """
        Upload a trial deployment to ThingsBoard.

        Delegates to :meth:`loadTrialToThingsboard`.

        Parameters
        ----------
        trialSetName : str
            The trial set name (e.g., ``"deploy"``).
        trialName : str
            The trial name.
        """
        self.loadTrialToThingsboard(trialSetName, trialName)


    def loadTrialToThingsboard(self, trialSetName: str, trialName: str):
        """
        Upload trial entity attributes to ThingsBoard.

        For each entity in the trial:

        1. Clears existing attributes in all scopes (SERVER, SHARED, CLIENT).
        2. Saves the trial's entity data as SERVER_SCOPE attributes.

        Parameters
        ----------
        trialSetName : str
            The trial set name.
        trialName : str
            The trial name within the set.
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
