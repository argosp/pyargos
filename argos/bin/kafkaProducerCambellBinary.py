import os
import argparse
from kafka import KafkaProducer
import time
import pandas
from hera import meteo
from argos.kafka import pandasSerializer


parser = argparse.ArgumentParser()
parser.add_argument("--file", dest="file", help="The binary data file path", required=True)
parser.add_argument("--kafkaHost", dest="kafkaHost", default='localhost', help="The kafka host in the following format - IP(:port)")
args = parser.parse_args()

producer = KafkaProducer(bootstrap_servers=args.kafkaHost)

try:
    lastUpdateTime = pandas.Timestamp.fromtimestamp(os.stat(args.file).st_mtime)
    flag = True
except FileNotFoundError:
    flag = False

cbi = meteo.CampbellBinaryInterface(args.file)
station = cbi.station
instrument = cbi.instrument
heights= cbi.heights


while True:
    while not flag:
        time.sleep(1)
        if os.path.exists(args.file):
            flag = True
            lastUpdateTime = pandas.Timestamp.fromtimestamp(os.stat(args.file).st_mtime)

    time.sleep(10)

    if not os.path.exists(args.file):
        flag = False
        continue

    tmpUpdateTime = pandas.Timestamp.fromtimestamp(os.stat(args.file).st_mtime)

    if True: #tmpUpdateTime!=lastUpdateTime:
        lastUpdateTime = tmpUpdateTime

        doc = meteo.CampbellBinary_datalayer.getDocFromDB(projectName=args.projectName, station=station, instrument=instrument, height=heights[0])
        lastTimeInDB = doc[0].getData().tail(1).index[0] if doc else cbi.firstTime

        # lastTimeInDB = pandas.Timestamp('2020-07-29 10:00:00.992000')

        newData, metadata = meteo.CampbellBinary_datalayer.parse(path=args.file, fromTime=lastTimeInDB)

        for height in heights:
            tmpNewData = newData.compute().query("station==@station and instrument==@instrument and height==@height").drop(columns=['station', 'instrument', 'height'])

            totalDelta = cbi.lastTime-lastTimeInDB

            timeSplit = pandas.date_range(lastTimeInDB, cbi.lastTime, totalDelta.seconds//180)
            for startTime, endTime in zip(timeSplit[:-1], timeSplit[1:]):
                print(startTime, endTime)
                message = pandasSerializer(tmpNewData[startTime:endTime])
                deviceName = '-'.join([station, instrument, str(height)])
                producer.send(deviceName, message)
                time.sleep(2)
                # import pdb
                # pdb.set_trace()
                print('-------- sent ---------\n', f'station - {station},', f'instrument - {instrument},', f'height - {height}')