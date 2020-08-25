from .. import pandasDataFrameSerializer, pandasSeriesSerializer
from hera import meteo


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
