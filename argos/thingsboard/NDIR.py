from numpy import random
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
from time import sleep

class NDIR:

    credential = None
    name = None
    manager = None

    def __init__(self,name,credential,manager):
        """
            Initialize the NDIR devices.
        Parameters
        ----------
        name  : string
            The name of the device.
        credential : string
            The thingsboard credential.
        restClient : argos experiment manager.
        """
        self.credential = credential
        self.name = name
        self.manager = manager
        tbConfiguration = self.manager.TBConfiguration
        self.device = TBDeviceMqttClient(tbConfiguration['mqttURL'], username=self.credential)
        self.device.connect()

    def __del__(self):
        self.device.disconnect()

    def publishMockDataMeasurement(self):
        """
            Send one mock data measurement
        Returns
        -------

        """

        min_v1000 = 0
        max_v1000 = 1000
        min_v50 = 0
        max_v50 = 50
        max_ppm1000 = 0
        min_ppm1000 = 1000
        max_ppm50 = 0
        min_ppm50 = 50


        values = {}
        values['v1000'] = min_v1000 + (max_v1000 - min_v1000) * random.rand()
        values['v50'] = min_v50 + (max_v50 - min_v50) * random.rand()
        values['ppm1000'] = min_ppm1000 + (max_ppm1000 - min_ppm1000) * random.rand()
        values['ppm50'] = min_ppm50 + (max_ppm50 - min_ppm50) * random.rand()
        if values['ppm1000'] > 50:
            values['ppm'] = values['ppm1000']
        else:
            values['ppm'] = values['ppm50']

        freq = random.normal(0.9,0.3)
        freq = 1 if freq>1 else freq
        freq = 0 if freq<0 else freq
        values['frequency'] =  freq
        self.device.send_telemetry(values)

class devicesNDIR:

    NDIRDict = None

    def __init__(self,manager):
        self.NDIRDict = dict()
        NDIRMap = manager.getDeviceMap("NDIR")

        for deviceName,deviceData in NDIRMap.items():
            self.NDIRDict[deviceName] = NDIR(name=deviceName,credential=deviceData['credential'],manager=manager)

    def publishMockDataMeasurements(self):
        while True:
            for ndir in self.NDIRDict.values():
                ndir.publishMockDataMeasurement()
            print("-----------------------------------------------------------------------")
            sleep(30)