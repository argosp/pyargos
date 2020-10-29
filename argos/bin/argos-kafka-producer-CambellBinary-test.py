import os
import argparse
from kafka import KafkaProducer
import time
import pandas
from hera import meteo
from argos.kafka import pandasSeriesSerializer
from multiprocessing import Pool


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", dest="file", help="The binary data file path", required=True)
    parser.add_argument("--projectName", dest="projectName", help="The project name", required=True)
    parser.add_argument("--kafkaHost", dest="kafkaHost", default='localhost',
                        help="The kafka host in the following format - IP(:port)")
    args = parser.parse_args()

    cbi = meteo.CampbellBinaryInterface(args.file)
    station = cbi.station
    instrument = cbi.instrument
    heights = cbi.heights

    def run(deviceName, data):
        print('run - %s' % deviceName)
        print(f'{data.index[0]} - {data.index[-1]}')
        producer = KafkaProducer(bootstrap_servers=args.kafkaHost)
        for timeIndex in data.index:
            message = pandasSeriesSerializer(data.loc[timeIndex])
            producer.send(deviceName, message)
            time.sleep(0.016)

    lastTimeProduced = None

    while lastTimeProduced is None or lastTimeProduced < cbi.lastTime:

        fromTime = cbi.firstTime if lastTimeProduced is None else cbi.getTimeByRecordIndex(cbi.getRecordIndexByTime(lastTimeProduced)+1)
        toTime = cbi.getTimeByRecordIndex(min(cbi.getRecordIndexByTime(fromTime) + 934 * 60, cbi.getRecordIndexByTime(cbi.lastTime)))

        print('------- Sending data --------')
        print(f'First time: {fromTime}')
        print(f'Last time: {toTime}')

        newData, metadata = meteo.CampbellBinary_datalayer.parse(path=args.file, fromTime=fromTime, toTime=toTime)

        runInput = []
        for height in heights:
            tmpNewData = newData.compute().query(
                "station==@station and instrument==@instrument and height==@height").drop(
                columns=['station', 'instrument', 'height'])
            deviceName = '-'.join([station, instrument, str(height)])
            runInput.append((deviceName, tmpNewData))

        with Pool(3) as p:
            p.starmap(run, runInput)

        lastTimeProduced = cbi.getTimeByRecordIndex(cbi.getRecordIndexByTime(toTime))
