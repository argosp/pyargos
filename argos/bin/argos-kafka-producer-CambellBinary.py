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


def waitFileToUpdate(file):
    tmpUpdateTime = pandas.Timestamp.utcfromtimestamp(os.stat(file).st_mtime)
    time.sleep(30)
    newUpdateTime = pandas.Timestamp.utcfromtimestamp(os.stat(file).st_mtime)
    while tmpUpdateTime!=newUpdateTime:
        tmpUpdateTime = newUpdateTime
        time.sleep(30)
        newUpdateTime = pandas.Timestamp.utcfromtimestamp(os.stat(file).st_mtime)
    print('File is fully updated')


def waitFileToUpdate2(file):
    cbi = meteo.CampbellBinaryInterface(file)
    tmpUpdateTime = cbi.lastTime
    time.sleep(30)
    cbi = meteo.CampbellBinaryInterface(file)
    while tmpUpdateTime!=cbi.lastTime:
        tmpUpdateTime = cbi.lastTime
        time.sleep(30)
        cbi = meteo.CampbellBinaryInterface(file)
    print('File is fully updated')


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

    print('First time in File %s' % cbi.firstTime)
    print('Last time in File %s' % cbi.lastTime)

    doc = meteo.CampbellBinary_datalayer.getDocFromDB(projectName=args.projectName, station=station,
                                                      instrument=instrument, height=heights[0])

    lastProducedTime = None

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
            print('New data: %s -------------------------------' % pandas.Timestamp.now())
            waitFileToUpdate2(args.file)
            cbi = meteo.CampbellBinaryInterface(args.file)
            if lastProducedTime is None:
                if doc:
                    lastTimeInDB = doc[0].getData().tail(1).index[0]
                    print('Last time in db - %s' % lastTimeInDB)
                    lastProducedTime = cbi.firstTime if cbi.firstTime > lastTimeInDB else lastTimeInDB
                    if lastProducedTime + pandas.Timedelta('45m') < cbi.lastTime:
                        startIndex = cbi.getRecordIndexByTime(
                            cbi.lastTime) - 934 * 60  # close to 30 minutes before last time in file
                        lastProducedTime = cbi.getTimeByRecordIndex(startIndex)
                else:
                    startIndex = cbi.getRecordIndexByTime(
                        cbi.lastTime) - 934 * 60  # close to 30 minutes before last time in file
                    lastProducedTime = cbi.firstTime if cbi.firstTime + pandas.Timedelta(
                        '30m') >= cbi.lastTime else cbi.getTimeByRecordIndex(startIndex)

            lastUpdateTime = tmpUpdateTime
            print('First time in File %s' % cbi.firstTime)
            print('Last time in File %s' % cbi.lastTime)
            print('Read file from %s' % lastProducedTime)
            # print('processing data from %s' % lastTimeInDB)
            # lastTimeInDB = pandas.Timestamp('2020-09-07 09:30:00')

            lastProducedTime = cbi.getTimeByRecordIndex(cbi.getRecordIndexByTime(lastProducedTime)+1)

            newData, metadata = meteo.CampbellBinary_datalayer.parse(path=args.file, fromTime=lastProducedTime)
            runInput = []
            for height in heights:
                tmpNewData = newData.compute().query("station==@station and instrument==@instrument and height==@height").drop(columns=['station', 'instrument', 'height'])
                deviceName = '-'.join([station, instrument, str(height)])
                runInput.append((deviceName, tmpNewData, args.kafkaHost))
                print(f"Sending {deviceName}: dates {tmpNewData.index[0]} to {tmpNewData.index[-1]}")



            with Pool(len(runInput)) as p:
                p.starmap(run, runInput)
