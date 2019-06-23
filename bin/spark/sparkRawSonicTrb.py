import sys
import json
import pandas
from datetime import datetime
from pyspark.sql import Row, SparkSession
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pymeteo.analytics.turbulencecalculator import TurbulenceCalculatorSpark
import paho.mqtt.client as mqtt
from pyargos.thingsboard.tbHome import tbHome

credentialMap = {}

connectionMap = {}
window_in_seconds = None

with open('/home/yehudaa/Projects/2019/DesertWalls/experimentConfiguration.json') as credentialOpen:
    credentialMap = json.load(credentialOpen)
tbh = tbHome(credentialMap["connection"])

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print("Connection failed")


def getClient(deviceName):
    if deviceName in connectionMap:
        client = connectionMap.get(deviceName, None)
    else:
        accessToken = tbh.deviceHome.createProxy(deviceName).getCredentials()
        client = mqtt.Client("Me")
        client.on_connect = on_connect

        client.username_pw_set(str(accessToken), password=None)
        try:
            client.connect(host=credentialMap['ip'])
        except:
            print('connection failed')
        print('connection succeed')
        connectionMap[deviceName] = client
        client.loop_start()
    return client


def getSparkSessionInstance(sparkConf):
    try:
        if ("sparkSessionSingletonInstance" not in globals()):
            globals()["sparkSessionSingletonInstance"] = SparkSession \
                .builder \
                .config(conf=sparkConf) \
                .getOrCreate()
        return globals()["sparkSessionSingletonInstance"]
    except:
        print('failed1')

def process(time, rdd):
    print("========= %s =========" % str(time))
    try:
        # Get the singleton instance of SparkSession
        spark = getSparkSessionInstance(rdd.context.getConf())

        # Convert RDD[String] to RDD[Row] to DataFrame
        rowRdd = rdd.map(lambda data: Row(Device=str(data['deviceName']),
                                          Time=datetime.fromtimestamp(float(data['ts']) / 1000.0),
                                          u=float(data['u']),
                                          v=float(data['v']),
                                          w=float(data['w']),
                                          T=float(data['T'])
                                          )
                         )
        wordsDataFrame = spark.createDataFrame(rowRdd)
        # print(wordsDataFrame.toPandas())
        for x in wordsDataFrame.toPandas().groupby("Device"):
            data = x[1].set_index('Time')[['T', 'u', 'v', 'w']]

            # print('----------%s----------'%(deviceName))
            resampledData = data.resample('%ds' % (window_in_seconds)).count()
            if (len(resampledData) > 2):
                deviceName = "%s_%ds" % (x[0], window_in_seconds)
                # deviceName = "Device_10s"
                startTime = pandas.datetime.time(resampledData.index[1])
                endTime = pandas.datetime.time(resampledData.index[1] + pandas.Timedelta('%ds' % (window_in_seconds)))
                data = data.between_time(startTime, endTime)
                trbCalc = TurbulenceCalculatorSpark(data, identifier={'samplingWindow': "%ds" % (window_in_seconds)}, metadata=None)
                calculatedParams = trbCalc.uu().vv().ww().compute()

                timeCalc = calculatedParams.index[0]
                values = calculatedParams.T.to_dict()[timeCalc]


                # print(timeCalc,values)
                client = getClient(deviceName)
                client.publish('v1/devices/me/telemetry', str({"ts": int(1000 * (datetime.timestamp(timeCalc))),
                                                               "values": values
                                                               }
                                                              )
                   )
    # wordsDataFrame.show()
    except Exception as e:
        print(e)

if __name__ == "__main__":

    # argparse
    # read the config file with the connection paramters.
    # use padnas timedelta to set windows_in_seconds with total_seconds().

    globals()
    windowInput = '10s'
    window_in_seconds = pandas.Timedelta(windowInput).seconds
    with open('/home/yehudaa/Projects/2019/testKafkaSpark/credentialMap.json') as credentialOpen:
        credentialMap = json.load(credentialOpen)
    sc = SparkContext(appName="PythonStreamingDirectKafkaWordCount")
    sc.setLogLevel("WARN")
    ssc = StreamingContext(sc, window_in_seconds)
    brokers, topic = sys.argv[1:]
    kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})
    lines = kvs.map(lambda x: x[1])
    linesAsJson = lines.map(lambda x: json.loads(x)).window(3 * window_in_seconds, window_in_seconds)
    try:
        linesAsJson.foreachRDD(process)
    except('Stop Iteration'):
        pass

    ssc.start()
    ssc.awaitTermination()
    for _, client in connectionMap:
        client.loop_stop()
        client.disconnect()