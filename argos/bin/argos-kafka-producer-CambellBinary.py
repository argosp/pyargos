import os
import argparse
from kafka import KafkaProducer
import time
import pandas
from hera import meteo
from argos.kafka import pandasSeriesSerializer, pandasDataFrameSerializer
from multiprocessing import Pool


def run(deviceName, data, kafkaHost):
    print('run - %s' % deviceName)
    producer = KafkaProducer(bootstrap_servers=kafkaHost)
    # totalDelta = data.index[-1]-data.index[0]
    # timeSplit = pandas.date_range(data.index[0], data.index[-1], totalDelta.seconds//10)

    # nowTime = pandas.Timestamp.now()
    # while nowTime.second!=data.index[0].second:
    #     nowTime = pandas.Timestamp.now()

    # for startTime, endTime in zip(timeSplit[:-1], timeSplit[1:]):
    #     if deviceName == 'Hamadpis-Raw_Sonic-16':
    #         print(startTime, '-', endTime)
    #     message = pandasDataFrameSerializer(data[startTime:endTime])
    #     producer.send(deviceName, message)
    #     time.sleep(10)
    for timeIndex in data.index:
        message = pandasSeriesSerializer(data.loc[timeIndex])
        producer.send(deviceName, message)
        time.sleep(0.016)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", dest="file", help="The binary data file path", required=True)
    parser.add_argument("--projectName", dest="projectName", help="The project name", required=True)
    parser.add_argument("--kafkaHost", dest="kafkaHost", default='localhost', help="The kafka host in the following format - IP(:port)")
    args = parser.parse_args()

    # try:
    #     lastUpdateTime = pandas.Timestamp.utcfromtimestamp(os.stat(args.file).st_mtime)
    #     flag = True
    # except FileNotFoundError:
    #     flag = False

    cbi = meteo.CampbellBinaryInterface(args.file)
    station = cbi.station
    instrument = cbi.instrument
    heights = cbi.heights

    while True:
        # while not flag:
        #     time.sleep(10)
        #     if os.path.exists(args.file):
        #         flag = True
        #         lastUpdateTime = pandas.Timestamp.utcfromtimestamp(os.stat(args.file).st_mtime)
        #
        # time.sleep(10)
        #
        # if not os.path.exists(args.file):
        #     flag = False
        #     continue
        #
        # tmpUpdateTime = pandas.Timestamp.utcfromtimestamp(os.stat(args.file).st_mtime)

        if True: #tmpUpdateTime!=lastUpdateTime:
            # print('new data')
            # lastUpdateTime = tmpUpdateTime
            #
            # doc = meteo.CampbellBinary_datalayer.getDocFromDB(projectName=args.projectName, station=station, instrument=instrument, height=heights[0])
            # lastTimeInDB = doc[0].getData().tail(1).index[0] if doc else cbi.firstTime
            # lastTimeInDB = cbi.firstTime if cbi.firstTime>lastTimeInDB else lastTimeInDB
            #
            # print('processing data from %s' % lastTimeInDB)
            lastTimeInDB = pandas.Timestamp('2020-07-29 09:30:00.992000')

            newData, metadata = meteo.CampbellBinary_datalayer.parse(path=args.file, fromTime=lastTimeInDB)
            runInput = []
            for height in heights:
                tmpNewData = newData.compute().query("station==@station and instrument==@instrument and height==@height").drop(columns=['station', 'instrument', 'height'])
                deviceName = '-'.join([station, instrument, str(height)])
                runInput.append((deviceName, tmpNewData, args.kafkaHost))
            with Pool(3) as p:
                p.starmap(run, runInput)
                # totalDelta = cbi.lastTime-lastTimeInDB
                #
                # timeSplit = pandas.date_range(lastTimeInDB, cbi.lastTime, totalDelta.seconds//10)
                # for startTime, endTime in zip(timeSplit[:-1], timeSplit[1:]):
                #     print(startTime, endTime)
                #     message = pandasDataFrameSerializer(tmpNewData[startTime:endTime])
                #     producer.send(deviceName, message)
                #     time.sleep(10)
                #     # import pdb
                #     # pdb.set_trace()
                #     print('-------- sent ---------\n')#, f'station - {station},', f'instrument - {instrument},', f'height - {height}')
                #
                # for timeIndex in tmpNewData.index:
                #     message = pandasSeriesSerializer(tmpNewData, timeIndex)
                #     producer.send(deviceName, message)
                #     time.sleep(0.03)
