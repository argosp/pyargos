import json
import sys
import pandas
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


def process(time, rdd):
    print("========= %s =========" % str(time))
    try:
        # Get the singleton instance of SparkSession
        spark = getSparkSessionInstance(rdd.context.getConf())

        # Convert RDD[String] to RDD[Row] to DataFrame
        rowRdd = rdd.map(lambda data: Row(Device=str(data['deviceName']),
                                          Time=pandas.datetime.fromtimestamp(float(data['ts']) / 1000.0),
                                          ppm2000=float(data['ppm2000']),
                                          ppm50=float(data['ppm50']),
                                          latitude=float(data['latitude']),
                                          longitude=float(data['longitude'])
                                          )
                         )
        wordsDataFrame = spark.createDataFrame(rowRdd)
        # print(wordsDataFrame.toPandas())
        for deviceName, deviceData in wordsDataFrame.toPandas().groupby("Device"):
            data = deviceData.set_index('Time')[['TCT']]
            countedData = data.resample('%ds' % (sliding_in_seconds)).count()
            if deviceName=='TCT1':
                print(countedData[['TCT']].rename(columns={'TCT': 'count'}))
            numOfTimeIntervals = len(countedData)
            numOfTimeIntervalsNeeded = int(window_in_seconds / sliding_in_seconds)
            if (numOfTimeIntervals >= numOfTimeIntervalsNeeded+2):
                windowDeviceName = '%s_%ds' % (deviceName, window_in_seconds)
                client = getClient(windowDeviceName)

                startTime = pandas.datetime.time(countedData.index[-numOfTimeIntervalsNeeded - 1])
                endTime = pandas.datetime.time(countedData.index[-1])
                data = data.between_time(startTime, endTime)
                resampledData = data.resample('%ds' % (window_in_seconds))
                dataToPublish = resampledData[['TCT']].count().rename(columns={'TCT': 'count'})

                meanData = resampledData.mean()
                stdData = resampledData.std()
                quantile10Data = resampledData.quantile(0.1)
                quantile25Data = resampledData.quantile(0.25)
                quantile50Data = resampledData.quantile(0.5)
                quantile75Data = resampledData.quantile(0.75)
                quantile90Data = resampledData.quantile(0.9)


                dataToPublish = dataToPublish.assign(TCT_mean=meanData['TCT'],
                                                     TCT_std=stdData['TCT'],
                                                     TCT_quantile10=quantile10Data['TCT'],
                                                     TCT_quantile25=quantile25Data['TCT'],
                                                     TCT_quantile50=quantile50Data['TCT'],
                                                     TCT_quantile75=quantile75Data['TCT'],
                                                     TCT_quantile90=quantile90Data['TCT'],
                                                     latitude=meanData['latitude'],
                                                     longitude=meanData['longitude'],
                                                     frequency=dataToPublish['count']/window_in_seconds
                                                     )

                values = dataToPublish.iloc[0].to_dict()

                # convertDataToITM(dataToPublish)

                client.publish('v1/devices/me/telemetry', str({"ts": int(1000 * (pandas.datetime.timestamp(countedData.index[-numOfTimeIntervalsNeeded-1]))),
                                                               "values": values
                                                               }
                                                              )
                               )
                # client.publish('v1/devices/me/attributes', str({'latitude':dataToPublish.iloc[1]['latitude'],
                #                                                 'longitude':dataToPublish.iloc[1]['longitude']
                #                                                 }
                #                                                )
                #                )
    except Exception as e:
        print(e)

if __name__ == "__main__":

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
