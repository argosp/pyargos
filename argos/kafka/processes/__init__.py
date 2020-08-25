import paho.mqtt.client as mqtt
from .. import pandasDataFrameSerializer, pandasSeriesSerializer
import logging
from argos import tbHome
from hera import meteo
import json
from kafka import KafkaProducer


def on_disconnect(client, userdata, rc=0):
    logging.debug("DisConnected result code " + str(rc))
    client.loop_stop()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print("Connection failed")


def calc_fluctuations(processor, data, windowFirstTime, topic):
    trc = meteo.getTurbulenceCalculator(data=data, samplingWindow=None)
    calculatedData = trc.fluctuations().compute()
    calculatedData.index = [windowFirstTime]
    message = pandasSeriesSerializer(calculatedData.iloc[0])
    processor.kafkaProducer.send(topic, message)


def to_thingsboard(processor, data, deviceName):
    client = processor.getClient(deviceName=deviceName)

    data.index = [x.tz_localize('israel') for x in data.index]
    client.publish('v1/devices/me/telemetry', pandasDataFrameSerializer(data))
    client.loop_stop()
    client.disconnect()
