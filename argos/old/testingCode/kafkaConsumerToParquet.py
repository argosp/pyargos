from kafka import KafkaConsumer
import argparse
import os
from hera import datalayer
import dask.dataframe
import warnings
from argos.old.kafka import toPandasDeserializer
import json


parser = argparse.ArgumentParser()
parser.add_argument("--topic", dest="topic" , help="The kafka topic to consume from", required=True)
parser.add_argument("--projectName", dest="projectName" , help="The project name", required=True)
parser.add_argument("--outputPath", dest="outputPath" , help="The saving path", required=True)
parser.add_argument("--kafkaHost", dest="kafkaHost", default="localhost", help="The kafka host in the following format - IP(:port)")
args = parser.parse_args()

consumer = KafkaConsumer(args.topic,
                         bootstrap_servers=[args.kafkaHost],
                         auto_offset_reset='latest',
                         enable_auto_commit=True,
                         group_id='my-group'
                         #value_deserializer=pandasDeserializer
                         )

deviceName = args.topic
station = deviceName.split('-')[0]
instrument = deviceName.split('-')[1]
height = int(deviceName.split('-')[2])
dir_path = os.path.join(args.outputPath, station, instrument, str(height))
desc = dict(station=station, instrument=instrument, height=height, DataSource='CampbellBinary')

_partition_size='100MB'

for message in consumer:
    #print('----------',pandas.Timestamp.fromtimestamp(message.timestamp/1000.0),'----------')
    try:
        new_dask = dask.dataframe.from_pandas(toPandasDeserializer(message.value), npartitions=1)
    except json.JSONDecodeError:
        print('esception')
        continue
    docList = datalayer.Measurements.getDocuments(projectName=args.projectName,
                                                  type='meteorological',
                                                  **desc
                                                  )

    # new_dask = groupby_data.get_group((station, instrument, height)) \
    #     .drop(columns=['station', 'instrument', 'height'])

    # for col in new_dask.columns:
    #     if new_dask[col].isnull().all().compute():
    #         new_dask = new_dask.drop(col, axis=1)

    if docList:
        if len(docList) > 1:
            raise ValueError("the list should be at max length of 1. Check your query.")
        else:

            # 3- get current data from database
            doc = docList[0]
            db_dask = doc.getData()
            data = [db_dask, new_dask]
            new_Data = dask.dataframe.concat(data, interleave_partitions=True) \
                                     .reset_index() \
                                     .drop_duplicates() \
                                     .set_index('index') \
                                     .repartition(partition_size=_partition_size)

            new_Data.to_parquet(doc.resource, engine='pyarrow')

            if doc.resource != dir_path:
                warnings.warn(
                    'The outputpath argument does not match the resource of the matching data '
                    'in the database.\nThe new data is saved in the resource of the matching '
                    'old data: %s' % doc.resource,
                    ResourceWarning)

    else:
        os.makedirs(dir_path, exist_ok=True)

        # 4- create meta data

        new_Data = new_dask.repartition(partition_size=_partition_size)
        new_Data.to_parquet(dir_path, engine='pyarrow')

        datalayer.Measurements.addDocument(projectName=args.projectName,
                                           resource=dir_path,
                                           dataFormat='parquet',
                                           type='meteorological',
                                           desc=desc
                                           )
