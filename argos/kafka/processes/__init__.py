from .. import pandasDataFrameSerializer
from hera import meteo
import dask.dataframe
from hera import datalayer
import os
import warnings


def calc_fluctuations(processor, data):
    trc = meteo.getTurbulenceCalculator(data=data, samplingWindow=None)
    calculatedData = trc.fluctuations().compute()
    calculatedData.index = [processor.currentWindowTime]
    message = pandasDataFrameSerializer(calculatedData)
    topicToSend = '%s-%s-%s' % (processor.topic, processor.window, processor.slide)
    processor.kafkaProducer.send(topicToSend, message)


def calc_wind(processor, data):
    trc = meteo.getTurbulenceCalculator(data=data, samplingWindow=None)
    calculatedData = trc.wind_speed().wind_dir_std().compute()
    calculatedData.index = [processor.currentWindowTime]
    message = pandasDataFrameSerializer(calculatedData)
    topicToSend = '%s-%s-%s' % (processor.topic, processor.window, processor.slide)
    processor.kafkaProducer.send(topicToSend, message)


def to_thingsboard(processor, data):
    client = processor.getClient(deviceName=processor.topic)

    data.index = [x.tz_localize('israel') for x in data.index]
    client.publish('v1/devices/me/telemetry', pandasDataFrameSerializer(data))


def to_parquet_CampbellBinary(processor, data, outputPath, _partition_size='100MB'):
    projectName = processor.projectName
    deviceName = processor.topic
    station = deviceName.split('-')[0]
    instrument = deviceName.split('-')[1]
    height = int(deviceName.split('-')[2])
    dir_path = os.path.join(outputPath, station, instrument, str(height))
    desc = dict(station=station, instrument=instrument, height=height, DataSource='CampbellBinary')
    new_dask = dask.dataframe.from_pandas(data, npartitions=1)

    docList = datalayer.Measurements.getDocuments(projectName=projectName,
                                                  type='meteorological',
                                                  **desc
                                                  )

    if docList:
        if len(docList) > 1:
            raise ValueError("the list should be at max length of 1. Check your query.")
        else:
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

        new_Data = new_dask.repartition(partition_size=_partition_size)
        new_Data.to_parquet(dir_path, engine='pyarrow')

        datalayer.Measurements.addDocument(projectName=projectName,
                                           resource=dir_path,
                                           dataFormat='parquet',
                                           type='meteorological',
                                           desc=desc
                                           )
