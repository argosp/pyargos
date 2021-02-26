from .. import pandasDataFrameSerializer
from hera import meteo
# from hera import experimentSetup
import dask.dataframe
import os
# import warnings
from kafka import KafkaProducer
import logging
import paho.mqtt.client as mqtt
import time
import pandas


def calc_wind(processor, data):
    print(f'calc wind - {processor.window}s')
    trc = meteo.getTurbulenceCalculator(data=data, samplingWindow=None)
    calculatedData = trc.wind_speed().wind_dir_std().compute()
    calculatedData.index = [processor.windowTime]
    message = pandasDataFrameSerializer(calculatedData)
    deviceName = '-'.join(processor.topic.split('-')[:-1])
    topicToSend = '%s-%s' % (deviceName, processor.window)
    producer = KafkaProducer(bootstrap_servers=processor.kafkaHost)
    producer.send(topicToSend, message)
    # processor.kafkaProducer.send(topicToSend, message)
    producer.flush()
    # time.sleep(1)


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
    print(f'to parquet - {processor.topic}')
    # print(data)
    new_data = data.copy()
    new_data['month'] = pandas.Timestamp(data.index[0]).month
    new_data['year'] = pandas.Timestamp(data.index[0]).year
    # raise EnvironmentError
    new_dask = dask.dataframe.from_pandas(new_data, npartitions=1)

    resource = processor.resource

    if os.path.isdir(resource):
        new_dask.to_parquet(path=resource,
                            append=True,
                            ignore_divisions=True,
                            engine='fastparquet',
                            partition_on=['year', 'month']
                            )
    else:
        os.makedirs(resource, exist_ok=True)
        new_dask.to_parquet(path=resource,
                            engine = 'fastparquet',
                            partition_on=['year', 'month']
                            )
