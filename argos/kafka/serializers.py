import json


def pandasDataFrameSerializer(df):
    """
    Serialize pandas.DataFrame to kafka message

    :param df:
    :return:
    """
    dataToSend = []
    for timeIndex in df.index:
        ts = int(timeIndex.timestamp() * 1000)
        dataToSend.append(dict(ts=ts, values=df.loc[timeIndex].to_dict()))
    message = json.dumps(dataToSend).encode('utf-8')
    return message


def pandasSeriesSerializer(series):
    """
    Serialize pandas.core.series.Series to kafka message

    :param df:
    :return:
    """
    ts = int(series.name.timestamp() * 1000)
    dataToSend = dict(ts=ts, values=series.to_dict())
    message = json.dumps(dataToSend).encode('utf-8')
    return message