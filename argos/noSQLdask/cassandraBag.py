from cassandra.cluster import Cluster
import dask
import dask.bag
import pandas
import numpy as np


class CassandraBag:

    def __init__(self, deviceID, IP='127.0.0.1', db_name='thingsboard', set_name='ts_kv_cf'):
        """

        :param IP: The IP of the noSQLdask host
        :param db_name: The name of the database
        :param set_name: The name of the data's table
        :param deviceID: The ID of the device
        """
        self.IP = IP
        self.db_name = db_name
        self.set_name = set_name
        self.deviceID = deviceID
        self.keys = self._keys()
        # self.partitions = self._partitions()

    def _keys(self):
        cluster = Cluster([self.IP])
        session = cluster.connect(self.db_name)
        keysQuery = "SELECT key FROM ts_kv_latest_cf WHERE entity_type='DEVICE' AND entity_id=%s" % (self.deviceID)
        keys_data_set = session.execute(keysQuery)
        session.shutdown()
        cluster.shutdown()

        keys_row_list = list(keys_data_set)
        keys = []
        for keys_row in keys_row_list:
            keys.append(keys_row.key)

        return keys

    def bag(self, start_time, end_time, npartitions=10):
        if type(start_time) == str:
            start_time = int(pandas.Timestamp(start_time).tz_localize("Israel").timestamp()*1000)
        if type(end_time) == str:
            end_time = int(pandas.Timestamp(end_time).tz_localize("Israel").timestamp()*1000)
        times = np.linspace(start_time, end_time, npartitions+1)
        partition_times = list(zip(times[0:-1], times[1:]))

        b = (dask.bag.from_sequence(partition_times)
                     .map(self._read_datetime_interval_from_set)
                     .flatten())
        return b

    def _read_datetime_interval_from_set(self, args):
        start_ts = int(args[0])
        end_ts = int(args[1])
        partitionsIntervals = self._splitTimesToPartitions(start_ts, end_ts)
        cluster = Cluster([self.IP])
        session = cluster.connect(self.db_name)
        items = []
        for key in list(self.keys):
            for partitionsInterval in partitionsIntervals:
                query = "SELECT ts,  key, dbl_v FROM %s WHERE entity_type='DEVICE' AND entity_id=%s AND key='%s' AND partition=%s AND ts>=%s AND ts<=%s" % (self.set_name, self.deviceID, key, str(partitionsInterval[0]),str(max(partitionsInterval[0], start_ts)), str(min(partitionsInterval[1], end_ts)))
                data_set = session.execute(query)
                items = items + list(data_set)
        session.shutdown()
        cluster.shutdown()
        return items

    def _splitTimesToPartitions(self, start_ts, end_ts):
        start_date = pandas.Timestamp.fromtimestamp(start_ts/1000.0)
        end_date = pandas.Timestamp.fromtimestamp(end_ts/1000.0)
        startPartitionTimestamp = pandas.Timestamp(year=start_date.year, month=start_date.month, day=1, unit='ms')#.tz_localize("Israel")
        if end_date.month == 12:
            endPartitionTimestamp = pandas.Timestamp(year=end_date.year, month=1, day=1, unit='ms')#.tz_localize("Israel")
        else:
            endPartitionTimestamp = pandas.Timestamp(year=end_date.year, month=end_date.month+1, day=1, unit='ms')#.tz_localize("Israel")
        partitions = self._ts_partitions(startPartitionTimestamp, endPartitionTimestamp)
        return list(zip(partitions[0:-1], partitions[1:]))

    def _ts_partitions(self, startTimestamp, endTimestamp):
        partitionsAsDate = [startTimestamp.date()]
        partitionsAsTs = [int(startTimestamp.timestamp()*1000)]
        while(partitionsAsDate[-1] != endTimestamp.date()):
            if partitionsAsDate[-1].month == 12:
                partitionTimestamp = pandas.Timestamp(year=partitionsAsDate[-1].year + 1, month=1, day=1, unit='ms')#.tz_localize("Israel")
            else:
                partitionTimestamp = pandas.Timestamp(year=partitionsAsDate[-1].year, month=partitionsAsDate[-1].month + 1, day=1, unit='ms')#.tz_localize("Israel")
            partitionsAsDate.append(partitionTimestamp.date())
            partitionsAsTs.append(int(partitionTimestamp.timestamp()*1000))
        return partitionsAsTs

    def getDataFrame(self, start_time, end_time, npartitions=10):
        bag = self.bag(start_time=start_time, end_time=end_time, npartitions=npartitions)
        df = bag.to_dataframe(meta={'ts': int, 'key': str, 'dbl_v': float})
        df = df.compute().pivot_table(index='ts',columns='key',values='dbl_v')
        return df


if __name__ == '__main__':
    cdb = CassandraBag(deviceID='727b0e40-5b96-11e9-989b-eb5e36f2a0b8', IP='100.100.100.10', db_name='thingsboard', set_name='ts_kv_cf')

    #start_time ='2019-06-17 14:00:00'
    #works fine
    # start_time = '2019-06-10'
    # end_time = '2019-06-15'

    start_time = '2019-07-20 00:00:00'
    end_time = '2019-07-21 00:00:00'
    partitions = 50

    bg = cdb.bag(start_time=start_time, end_time=end_time, npartitions=partitions)
    #bgDataFrame = bg.to_dataframe().set_index('Time')
    meta = {'ts':int, 'key':str, 'dbl_v':float}
    bgDataFrame = bg.to_dataframe(meta=meta)#.categorize(columns=['key']).pivot_table(index='ts',columns='key',values='dbl_v')
    df = bgDataFrame.compute().pivot_table(index='ts',columns='key',values='dbl_v')
    df.index = [pandas.Timestamp.fromtimestamp(x/1000.0) for x in df.index]
    #df.index = pandas.to_datetime(df.index, unit='ms')
    df.to_csv('/tmp/data.csv')
    #print(bgDataFrame.compute())
    #bgDataFrame.index = bgDataFrame.index.map(tsToDate, meta=('ts','i8')) ------ not working ------
