import json
import sys
import pandas
from pyproj import Proj
from pyproj import transform
from datetime import datetime
from pyspark.sql import Row, SparkSession
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import paho.mqtt.client as mqtt
from pyargos.thingsboard.tbHome import tbHome

credentialMap = {}

connectionMap = {}
window_in_seconds = None

with open('/home/yehudaa/Projects/2019/TestExp/experimentConfiguration.json') as credentialOpen:
    credentialMap = json.load(credentialOpen)

def convertToITM(lon, lat):
    ITM_Proj = Proj('+proj=tmerc +lat_0=31.734393611111113 +lon_0=35.20451694444445 +k=1.0000067 +x_0=219529.584 +y_0=626907.39 +ellps=GRS80 +towgs84=-24.002400,-17.103200,-17.844400,-0.33077,-1.852690,1.669690,5.424800 +units=m +no_defs')
    GRS80_Proj = Proj('+init=EPSG:4326')
    x, y = transform(GRS80_Proj, ITM_Proj, lon, lat)
    return x, y

def convertDataToITM(data):
    for time in data.index:
        latitude, longitude = convertToITM(data.loc[time]['longitude'] ,data.loc[time]['latitude'])
        data.at[time, 'longitude'] = longitude
        data.at[time, 'latitude'] = latitude

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print("Connection failed")

def getClient(deviceName):
    if deviceName in connectionMap:
        client = connectionMap[deviceName]
    else:
        tbh = tbHome(credentialMap["connection"])
        accessToken = tbh.deviceHome.createProxy(deviceName).getCredentials()
        client = mqtt.Client("Me")
        client.on_connect = on_connect

        client.username_pw_set(str(accessToken), password=None)
        try:

            client.connect(host=credentialMap["connection"]['server']['ip'],port=1883)
        except Exception as e:
            print(e)
            print('connection failed')
            raise e

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
                                          longitude=float(data['longitude']),
                                          latitude=float(data['latitude'])
                                          ) if('latitude' in data.keys() and 'longitude' in data.keys()) else Row(Device=str(data['deviceName']),
                                          Time=datetime.fromtimestamp(float(data['ts']) / 1000.0), longitude=None, latitude=None)
                         )
        wordsDataFrame = spark.createDataFrame(rowRdd)
        wordsDataFrame.dropna()
        # print(wordsDataFrame.toPandas())
        for deviceName, deviceData in wordsDataFrame.toPandas().groupby("Device"):
            data = deviceData.set_index('Time')[['longitude', 'latitude']]
            convertDataToITM(data)
            # print('----------%s----------'%(deviceName))
            resampledData = data.resample('%ds' % (window_in_seconds))
            dataToPublish = resampledData.mean()
            if (len(dataToPublish) > 2):
                timeCalc = dataToPublish.index[1]
                values = dataToPublish.iloc[1].to_dict()

                # print(timeCalc,values)
                windowDeviceName = '%s_10s' % deviceName
                client = getClient(windowDeviceName)
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
    windowInput = '60s'
    window_in_seconds = pandas.Timedelta(windowInput).seconds


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
