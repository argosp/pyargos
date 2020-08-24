import pandas
import paho.mqtt.client as mqtt
from .. import toPandasDeserializer, pandasDataFrameSerializer, pandasSeriesSerializer
import logging
from argos import tbHome
from hera import meteo
import json
from kafka import KafkaProducer
import time


def on_disconnect(client, userdata, rc=0):
    logging.debug("DisConnected result code " + str(rc))
    client.loop_stop()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print("Connection failed")

def print_mean_T(data):
    if data is not None:
        print('Mean T - ', data['T'].mean())

def send_kafka(data, topic, kafkaHost):
    producer = KafkaProducer(bootstrap_servers=kafkaHost)
    message = pandasDataFrameSerializer(data)
    producer.send(topic, message)

def calc_fluctuations(data, topic, kafkaHost='localhost'):
    trc = meteo.getTurbulenceCalculator(data=data, samplingWindow=None)
    calculatedData = trc.fluctuations().compute()
    send_kafka(data=data, topic=topic, kafkaHost=kafkaHost)
    # print(calculatedData)

def to_thingsboard(data, deviceName, tbHost='localHost', expConf='/home/eden/Projects.local/2019/DesertWalls/experimentConfiguration.json'):
    with open(expConf, 'r') as credentialOpen:  # with open(args.expConf)
        credentialMap = json.load(credentialOpen)
    tbh = tbHome(credentialMap["connection"])

    #deviceName = 'producerTest'

    client = mqtt.Client("Me_%s" % deviceName)
    accessToken = tbh.deviceHome.createProxy(deviceName).getCredentials()
    client.username_pw_set(accessToken, password=None)
    client.on_disconnect = on_disconnect
    client.connect(tbHost)
    client.loop_start()

    data.index = [x.tz_localize('israel') for x in data.index]
    client.publish('v1/devices/me/telemetry', pandasDataFrameSerializer(data))



def print_fluctuations2(data, deviceName, tbHost='localHost', expConf='/home/eden/Projects.local/2019/DesertWalls/experimentConfiguration.json'):
    with open(expConf, 'r') as credentialOpen:  # with open(args.expConf)
        credentialMap = json.load(credentialOpen)
    tbh = tbHome(credentialMap["connection"])

    #deviceName = 'producerTest'

    client = mqtt.Client("Me_%s" % deviceName)
    accessToken = tbh.deviceHome.createProxy(deviceName).getCredentials()
    client.username_pw_set(accessToken, password=None)
    client.on_disconnect = on_disconnect
    client.connect(tbHost)
    client.loop_start()

    trc = meteo.getTurbulenceCalculator(data=data, samplingWindow=None)
    calculatedData = trc.fluctuations().compute()
    calculatedData.index = [x.tz_localize('israel') for x in calculatedData.index]
    print(calculatedData)
    client.publish('v1/devices/me/telemetry', pandasDataFrameSerializer(calculatedData))

def print_sliding_window_old(consumer, window, slide):
    print(window, '---', slide)

    df = pandas.DataFrame()
    lastTime = None
    n = int(window/slide)

    for message in consumer:
        df = df.append(toPandasDeserializer(message.value), sort=True)
        if lastTime is None:
            lastTime = df.index[0]
            resampled_df = df.resample('%ss' % slide)
        elif lastTime + pandas.Timedelta('%ss' % slide) < df.tail(1).index[0]:
            resampled_df = df.resample('%ss' % slide)
        timeList = list(resampled_df.groups.keys())
        if len(timeList) > n:
            try:
                if lastTime != timeList[0]:
                    lastTime = timeList[0]
                    print('Mean T - ', resampled_df.get_group(timeList[0]).mean()['T'])
                    # import pdb
                    # pdb.set_trace()
                    df = df[timeList[1]:]
            except Exception as exception:
                print(f'Exception {exception} handled')


def publish_sliding_window_fluctuations_old(consumer, window, slide, deviceName, tbHost='localhost', expConf='/home/eden/Projects.local/2019/DesertWalls/experimentConfiguration.json'):
    print(window, '---', slide, '---', 'fluctuations')

    with open(expConf, 'r') as credentialOpen:  # with open(args.expConf)
        credentialMap = json.load(credentialOpen)
    tbh = tbHome(credentialMap["connection"])

    #deviceName = 'producerTest'

    client = mqtt.Client("Me_%s" % deviceName)
    accessToken = tbh.deviceHome.createProxy(deviceName).getCredentials()
    client.username_pw_set(accessToken, password=None)
    client.on_disconnect = on_disconnect
    client.connect(tbHost)
    client.loop_start()

    df = pandas.DataFrame()
    lastTime = None
    n = int(window / slide)

    for message in consumer:
        df = df.append(toPandasDeserializer(message.value), sort=True)
        if lastTime is None:
            lastTime = df.index[0]
            resampled_df = df.resample('%ss' % slide)
        elif lastTime + pandas.Timedelta('%ss' % slide) < df.tail(1).index[0]:
            resampled_df = df.resample('%ss' % slide)
        timeList = list(resampled_df.groups.keys())
        if len(timeList) > n:
            try:
                if lastTime != timeList[0]:
                    lastTime = timeList[0]
                    data = resampled_df.get_group(timeList[0])
                    data.index = [lastTime if i==0 else data.index[i] for i in range(len(data.index))]
                    trc = meteo.getTurbulenceCalculator(data=data, samplingWindow=None)
                    calculatedData = trc.fluctuations().compute()
                    calculatedData.index = [x.tz_localize('israel') for x in calculatedData.index]
                    print(calculatedData)
                    client.publish('v1/devices/me/telemetry', pandasDataFrameSerializer(calculatedData))
                    # import pdb
                    # pdb.set_trace()
                    df = df[timeList[1]:]
            except Exception as exception:
                print(f'Exception {exception} handled')
