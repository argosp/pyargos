from .. import pandasDataFrameSerializer
from hera import meteo
# from hera import datalayer
import dask.dataframe
import os
# import warnings
from kafka import KafkaProducer
import logging
import paho.mqtt.client as mqtt
import time


def calc_wind(processor, data):
    print(f'calc wind - {processor.window}s')
    trc = meteo.getTurbulenceCalculator(data=data, samplingWindow=None)
    calculatedData = trc.wind_speed().wind_dir_std().compute()
    calculatedData.index = [processor.windowTime]
    message = pandasDataFrameSerializer(calculatedData)
    topicToSend = '%s-%s' % (processor.baseName, processor.window)
    producer = KafkaProducer(bootstrap_servers=processor.kafkaHost)
    producer.send(topicToSend, message)
    producer.flush()


def to_thingsboard(processor, data):
    def on_disconnect(client, userdata, rc=0):
        logging.debug("DisConnected result code " + str(rc))
        client.loop_stop()

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
        else:
            print("Connection failed")

    def getClient():
        if processor.client is None:
            devices = processor.tbh.deviceHome.getAllEntitiesName()
            if processor.topic in devices:
                #print('Connecting to %s' % deviceName)
                client = mqtt.Client("Me_%s" % processor.topic)
                client.on_connect = on_connect

                accessToken = processor.tbh.deviceHome.createProxy(processor.topic).getCredentials()
                client.username_pw_set(accessToken, password=None)
                client.on_disconnect = on_disconnect
                client.connect(host=processor.tbHost, port=1883)
                client.loop_start()
                processor.setClient(client)
                time.sleep(0.01)
        else:
            client = processor.client

        return client

    print(f'to thingsboard - {processor.topic}')
    # print(data)

    data.index = [x.tz_localize('israel') for x in data.index]
    getClient().publish('v1/devices/me/telemetry', pandasDataFrameSerializer(data))


def to_parquet_CampbellBinary(processor, data):
    print(f'to parquet - {processor.baseName}')
    # print(data)
    new_dask = dask.dataframe.from_pandas(data, npartitions=1)

    resource = processor.resource

    if os.path.isdir(resource):
        new_dask.to_parquet(path=resource,
                            append=True,
                            ignore_divisions=True,
                            engine='pyarrow'
                            )
    else:
        os.makedirs(resource, exist_ok=True)
        new_dask.to_parquet(path=resource,
                            engine = 'pyarrow'
                            )
