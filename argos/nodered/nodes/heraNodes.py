import os
import json
import pandas
import dask.dataframe as dd
import pandas
from pynodered import node_red, NodeProperty

@node_red(category="argos",
          properties=dict(outputDirectory=NodeProperty("Output Directory", value=""),
                          timestampField  =NodeProperty("Timestamp field", value="timestamp"),
                          fileNameField  =NodeProperty("filename field", value=""),
                          partitionaFields=NodeProperty("Partition on", value=""))
          )
def to_parquet(node,msgList):

    def saveParquetToFile(filename,data):
        print(filename)

        if os.path.isdir(filename):

            data.to_parquet(path=filename,
                                append=True,
                                ignore_divisions=True,
                                engine='fastparquet',
                                partition_on=partitionaFields
                           )
        else:

            os.makedirs(filename, exist_ok=True)
            data.to_parquet(path=filename,
                                engine = 'fastparquet',
                                partition_on=partitionaFields
                                )

    timestampField = "timestamp" if (node.timestampField.value=="") else node.timestampField.value
    fileNameField  = "deviceName" if (node.fileNameField.value=="") else node.fileNameField.value

    outputDirectory = node.outputDirectory.value

    if (node.fileNameField.value==""):
        partitionaFields =['year', 'month']
    else:
        partitionaFields = node.fileNameField.value.split(",")



    df = pandas.DataFrame(msgList['payload'])
    df[timestampField] = df[timestampField].astype('datetime64[ns]')

    df = df.assign(day=df.timestamp.apply(lambda x: x.day))\
           .assign(month=df.timestamp.apply(lambda x: x.month)) \
           .assign(year=df.timestamp.apply(lambda x: x.year))

    df = df.set_index("timestamp")

    if node.fileNameField.value =="":

        new_dask = dd.from_pandas(df, npartitions=1)
        saveParquetToFile(outputDirectory, new_dask)

    else:

        for grpname,grpdata in df.groupby(fileNameField):

            filename=os.path.join(outputDirectory,f"{grpname}.parquet")

            new_dask = dd.from_pandas(grpdata, npartitions=1)
            saveParquetToFile(filename,new_dask)


