#! /usr/bin/env python

import os
import argparse
from kafka import KafkaProducer
import time
import pandas
from hera import meteo
from argos.kafka import pandasSeriesSerializer
from multiprocessing import Pool


def run(deviceName, deviceType, data, kafkaHost):
    print('run - %s' % deviceName)
    producer = KafkaProducer(bootstrap_servers=kafkaHost)
    data = globals()['fix_%s' % deviceType](data)
    for timeIndex in data.index:
        message = pandasSeriesSerializer(data.loc[timeIndex])
        producer.send(deviceName, message)
        time.sleep(0.016)


def waitFileToUpdate(file):
    tmpUpdateTime = pandas.Timestamp.utcfromtimestamp(os.stat(file).st_mtime)
    time.sleep(30)
    newUpdateTime = pandas.Timestamp.utcfromtimestamp(os.stat(file).st_mtime)
    # Check that file firstly updated
    while tmpUpdateTime==newUpdateTime:
        tmpUpdateTime = newUpdateTime
        time.sleep(10)
        newUpdateTime = pandas.Timestamp.utcfromtimestamp(os.stat(file).st_mtime)
    # Check that file is fuly updated
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
    # Check that file firstly updated
    while tmpUpdateTime==cbi.lastTime:
        tmpUpdateTime = cbi.lastTime
        time.sleep(10)
        cbi = meteo.CampbellBinaryInterface(file)
    # Check that file is fuly updated
    while tmpUpdateTime!=cbi.lastTime:
        tmpUpdateTime = cbi.lastTime
        time.sleep(30)
        cbi = meteo.CampbellBinaryInterface(file)
    print('File is fully updated')
    return pandas.Timestamp.utcfromtimestamp(os.stat(file).st_mtime)


def fix_Young81000(data):
    data['v'] = -data['v']
    data['u'] = -data['u']
    return data


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", dest="file", help="The binary data file path", required=True)
    parser.add_argument("--projectName", dest="projectName", help="The project name", required=True)
    parser.add_argument("--deviceType", dest="deviceType", help="The device name to know how to fix the data", required=True)
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
            lastUpdateTime = waitFileToUpdate2(args.file)
            cbi = meteo.CampbellBinaryInterface(args.file)

            print('Last produced time: %s' % lastProducedTime)
            print('First time in File %s' % cbi.firstTime)
            print('Last time in File %s' % cbi.lastTime)

            if lastProducedTime is None:
                if doc:
                    lastTimeInDB = doc[0].getData().tail(1).index[0]
                    print('Last time in db - %s' % lastTimeInDB)
                    fromTime = cbi.firstTime if cbi.firstTime > lastTimeInDB else cbi.getTimeByRecordIndex(cbi.getRecordIndexByTime(lastTimeInDB)+1)
                    if fromTime + pandas.Timedelta('35m') < cbi.lastTime:
                        startIndex = cbi.getRecordIndexByTime(
                            cbi.lastTime) - 934 * 60  # close to 30 minutes before last time in file
                        fromTime = cbi.getTimeByRecordIndex(startIndex)
                else:
                    startIndex = cbi.getRecordIndexByTime(
                        cbi.lastTime) - 934 * 60  # close to 30 minutes before last time in file
                    fromTime = cbi.firstTime if cbi.firstTime + pandas.Timedelta(
                        '30m') >= cbi.lastTime else cbi.getTimeByRecordIndex(startIndex)
            else:
                fromTime = cbi.getTimeByRecordIndex(cbi.getRecordIndexByTime(lastProducedTime)+1)


            # print('processing data from %s' % lastTimeInDB)
            # lastTimeInDB = pandas.Timestamp('2020-09-07 09:30:00')

            print('Read file from %s' % fromTime)

            newData, metadata = meteo.CampbellBinary_datalayer.parse(path=args.file, fromTime=fromTime)
            runInput = []
            for height in heights:
                tmpNewData = newData.compute().query("station==@station and instrument==@instrument and height==@height").drop(columns=['station', 'instrument', 'height'])
                deviceName = '-'.join([station, instrument, str(height)])
                runInput.append((deviceName, args.deviceType, tmpNewData, args.kafkaHost))
                print(f"Sending {deviceName}: dates {tmpNewData.index[0]} to {tmpNewData.index[-1]}")

            with Pool(len(runInput)) as p:
                p.starmap(run, runInput)

            print('---------- Done ----------')

            lastProducedTime = cbi.getTimeByRecordIndex(cbi.getRecordIndexByTime(cbi.lastTime))
