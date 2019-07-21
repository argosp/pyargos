import json
import sys
import pandas
from datetime import datetime
from pyspark.sql import Row, SparkSession
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import paho.mqtt.client as mqtt
from pyargos.thingsboard.tbHome import tbHome
import argparse
from pyproj import Proj, transform

credentialMap = {}

connectionMap = {}
window_in_seconds = None
maxMap = {}
dosageMap = {}

# with open('/home/yehudaa/Projects/2019/TestExp/experimentConfiguration.json', 'r') as credentialOpen:
#     credentialMap = json.load(credentialOpen)

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


def _calcPPM(ppm50, ppm1000):
    ppm = []
    for i in range(len(ppm50)):
        ppm.append(ppm50[i] if ppm1000[i]<=50 else ppm1000[i])
    return ppm

def process(time, rdd):
    print("========= %s =========" % str(time))
    try:
        # Get the singleton instance of SparkSession
        spark = getSparkSessionInstance(rdd.context.getConf())

        # Convert RDD[String] to RDD[Row] to DataFrame
        rowRdd = rdd.map(lambda data: Row(Device=str(data['deviceName']),
                                          Time=datetime.fromtimestamp(float(data['ts']) / 1000.0),
                                          ppm1000=float(data['ppm1000']),
                                          ppm50=float(data['ppm50']),
                                          latitude=float(data['latitude']),
                                          longitude=float(data['longitude'])
                                          )
                         )
        wordsDataFrame = spark.createDataFrame(rowRdd)
        # print(wordsDataFrame.toPandas())
        for deviceName, deviceData in wordsDataFrame.toPandas().groupby("Device"):
            data = deviceData.set_index('Time')[['ppm1000', 'ppm50', 'latitude', 'longitude']]
            data['ppm'] = _calcPPM(data['ppm50'].values, data['ppm1000'].values)
            # print('----------%s----------'%(deviceName))
            resampledData = data.resample('%ds' % (window_in_seconds))
            dataToPublish = resampledData[['ppm']].count().rename(columns={'ppm': 'count'})
            if (len(dataToPublish) > 2):
                windowDeviceName = '%s_%ds' % (deviceName, window_in_seconds)
                client = getClient(windowDeviceName)

                meanData = resampledData.mean()
                stdData = resampledData.std()
                quantile1Data = resampledData.quantile(0.1)
                quantile9Data = resampledData.quantile(0.9)

                lastMax = maxMap.setdefault(deviceName, 0)
                maxMap[deviceName] = max(lastMax, resampledData.max().iloc[1]['ppm'])
                lastDosage = dosageMap.setdefault(deviceName, 0)
                dosageMap[deviceName] = lastDosage + window_in_seconds*meanData.iloc[1]['ppm']

                dataToPublish = dataToPublish.assign(ppm1000_mean=meanData['ppm1000'],
                                                     ppm50_mean=meanData['ppm50'],
                                                     ppm_mean=meanData['ppm'],
                                                     ppm1000_std=stdData['ppm1000'],
                                                     ppm50_std=stdData['ppm50'],
                                                     ppm_std=stdData['ppm'],
                                                     ppm1000_quantile1=quantile1Data['ppm1000'],
                                                     ppm50_quantile1=quantile1Data['ppm50'],
                                                     ppm_quantile1=quantile1Data['ppm'],
                                                     ppm1000_quantile9=quantile9Data['ppm1000'],
                                                     ppm50_quantile9=quantile9Data['ppm50'],
                                                     ppm_quantile9=quantile9Data['ppm'],
                                                     ppm_max=maxMap[deviceName],
                                                     ppm_dosage=dosageMap[deviceName],
                                                     # latitude=meanData['latitude'],
                                                     # longitude=meanData['longitude'],
                                                     frequency=dataToPublish['count']/window_in_seconds
                                                     )

                timeCalc = dataToPublish.index[1]
                values = dataToPublish.iloc[1].to_dict()

                # convertDataToITM(dataToPublish)

                # print(timeCalc,values)

                client.publish('v1/devices/me/telemetry', str({"ts": int(1000 * (datetime.timestamp(timeCalc))),
                                                               "values": values
                                                               }
                                                              )
                               )
                client.publish('v1/devices/me/attributes', str({'latitude':dataToPublish.iloc[1]['latitude'],
                                                                'longitude':dataToPublish.iloc[1]['longitude']
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

    parser = argparse.ArgumentParser()
    parser.add_argument("--sparkConf", dest="sparkConf", help="The spark configuration json", required=True)
    args = parser.parse_args()

    with open(args.sparkConf, "r") as sparkConfFile:
        sparkConf = json.load(sparkConfFile)

    window_in_seconds = pandas.Timedelta(sparkConf['window']).seconds
    sliding_in_seconds = pandas.Timedelta(sparkConf['slidingWindow']).seconds

    with open(sparkConf['expConf'], "r") as expConf:
        credentialMap = json.load(expConf)

    sc = SparkContext(appName="PythonStreamingDirectKafkaWordCount")
    sc.setLogLevel("WARN")
    ssc = StreamingContext(sc, 10)
    brokers = sparkConf['broker']
    topic = sparkConf['topic']
    kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})
    lines = kvs.map(lambda x: x[1])
    linesAsJson = lines.map(lambda x: json.loads(x)).window(20 + window_in_seconds, sliding_in_seconds)
    try:
        linesAsJson.foreachRDD(process)
    except('Stop Iteration'):
        pass

    ssc.start()
    ssc.awaitTermination()
    for _, client in connectionMap:
        client.loop_stop()
        client.disconnect()
