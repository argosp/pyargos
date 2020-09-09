#! /usr/bin/env python

import os
import argparse
from kafka import KafkaProducer
import time
import pandas
from hera import meteo
from argos.kafka import pandasSeriesSerializer
from multiprocessing import Pool


def run(deviceName, data, kafkaHost):
    print('run - %s' % deviceName)
    producer = KafkaProducer(bootstrap_servers=kafkaHost)
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

    try:
        lastUpdateTime = pandas.Timestamp.utcfromtimestamp(os.stat(args.file).st_mtime)
        flag = True
    except FileNotFoundError:
        flag = False

    cbi = meteo.CampbellBinaryInterface(args.file)
    station = cbi.station
    instrument = cbi.instrument
    heights = cbi.heights

    while True:
        while not flag:
            time.sleep(10)
            if os.path.exists(args.file):
                flag = True
                lastUpdateTime = pandas.Timestamp.utcfromtimestamp(os.stat(args.file).st_mtime)

        time.sleep(10)

        if not os.path.exists(args.file):
            flag = False
            continue

        tmpUpdateTime = pandas.Timestamp.utcfromtimestamp(os.stat(args.file).st_mtime)

        if tmpUpdateTime!=lastUpdateTime: # True
            # print('new data')
            lastUpdateTime = tmpUpdateTime

            doc = meteo.CampbellBinary_datalayer.getDocFromDB(projectName=args.projectName, station=station, instrument=instrument, height=heights[0])
            if doc:
                lastTimeInDB = doc[0].getData().tail(1).index[0]
                lastTimeInDB = cbi.firstTime if cbi.firstTime > lastTimeInDB else lastTimeInDB
                if lastTimeInDB+pandas.Timedelta('30m')<cbi.lastTime:
                    startIndex = cbi.getRecordIndexByTime(cbi.lastTime) - 934 * 60 # close to 30 minutes before last time in file
                    lastTimeInDB = cbi.getTimeByRecordIndex(startIndex)
            else:
                startIndex = cbi.getRecordIndexByTime(cbi.lastTime)-934*60 # close to 30 minutes before last time in file
                lastTimeInDB = cbi.firstTime if cbi.firstTime+pandas.Timedelta('30m')>=cbi.lastTime else cbi.getTimeByRecordIndex(startIndex)

            # print('processing data from %s' % lastTimeInDB)
            # lastTimeInDB = pandas.Timestamp('2020-09-07 09:30:00')

            newData, metadata = meteo.CampbellBinary_datalayer.parse(path=args.file, fromTime=lastTimeInDB)
            runInput = []
            for height in heights:
                tmpNewData = newData.compute().query("station==@station and instrument==@instrument and height==@height").drop(columns=['station', 'instrument', 'height'])
                deviceName = '-'.join([station, instrument, str(height)])
                runInput.append((deviceName, tmpNewData, args.kafkaHost))
            with Pool(3) as p:
                p.starmap(run, runInput)
