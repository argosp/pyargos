"""
Dask-based interface to Cassandra time-series data.

Provides the ``CassandraBag`` class for querying device telemetry from
a Cassandra database (typically the ThingsBoard backend) using Dask
for parallel, partitioned reads.
"""

from cassandra.cluster import Cluster
import dask
import dask.bag
import pandas
import numpy as np


class CassandraBag:
    """
    Dask bag interface for querying Cassandra time-series data.

    Designed for querying the ThingsBoard ``ts_kv_cf`` table, which stores
    device telemetry as key-value pairs partitioned by month.

    Parameters
    ----------
    deviceID : str
        The UUID of the device to query.
    IP : str, optional
        The Cassandra node IP address. Defaults to ``"127.0.0.1"``.
    db_name : str, optional
        The database (keyspace) name. Defaults to ``"thingsboard"``.
    set_name : str, optional
        The table name. Defaults to ``"ts_kv_cf"``.

    Examples
    --------
    >>> bag = CassandraBag(deviceID="727b0e40-5b96-11e9-989b-eb5e36f2a0b8")
    >>> df = bag.getDataFrame("2024-01-01", "2024-01-31")
    """

    def __init__(self, deviceID, IP='127.0.0.1', db_name='thingsboard', set_name='ts_kv_cf'):
        """
        Initialize CassandraBag and fetch available metric keys.

        Parameters
        ----------
        deviceID : str
            The UUID of the device to query.
        IP : str, optional
            The Cassandra node IP address. Defaults to ``"127.0.0.1"``.
        db_name : str, optional
            The database (keyspace) name. Defaults to ``"thingsboard"``.
        set_name : str, optional
            The table name. Defaults to ``"ts_kv_cf"``.
        """
        self.IP = IP
        self.db_name = db_name
        self.set_name = set_name
        self.deviceID = deviceID
        self.keys = self._keys()

    def _keys(self):
        """Fetch available metric keys for the device from ts_kv_latest_cf."""
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
        """
        Create a Dask bag for parallel reads over a time range.

        Splits the time range into ``npartitions`` equal intervals and
        creates a Dask bag that reads each interval in parallel.

        Parameters
        ----------
        start_time : str or int
            Start of the time range. Accepts date strings (e.g.,
            ``"2024-01-01"``) or millisecond timestamps.
        end_time : str or int
            End of the time range. Same format as ``start_time``.
        npartitions : int, optional
            Number of parallel partitions. Defaults to 10.

        Returns
        -------
        dask.bag.Bag
            A Dask bag of ``(ts, key, dbl_v)`` named tuples, suitable
            for further processing or conversion to DataFrame.
        """
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
        """Read data for a single time interval from Cassandra, handling monthly partitions."""
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
        """Split a time range into monthly Cassandra partition boundaries."""
        start_date = pandas.Timestamp.fromtimestamp(start_ts/1000.0)
        end_date = pandas.Timestamp.fromtimestamp(end_ts/1000.0)
        startPartitionTimestamp = pandas.Timestamp(year=start_date.year, month=start_date.month, day=1, unit='ms')
        if end_date.month == 12:
            endPartitionTimestamp = pandas.Timestamp(year=end_date.year, month=1, day=1, unit='ms')
        else:
            endPartitionTimestamp = pandas.Timestamp(year=end_date.year, month=end_date.month+1, day=1, unit='ms')
        partitions = self._ts_partitions(startPartitionTimestamp, endPartitionTimestamp)
        return list(zip(partitions[0:-1], partitions[1:]))

    def _ts_partitions(self, startTimestamp, endTimestamp):
        """Generate a list of monthly partition timestamps between start and end."""
        partitionsAsDate = [startTimestamp.date()]
        partitionsAsTs = [int(startTimestamp.timestamp()*1000)]
        while(partitionsAsDate[-1] != endTimestamp.date()):
            if partitionsAsDate[-1].month == 12:
                partitionTimestamp = pandas.Timestamp(year=partitionsAsDate[-1].year + 1, month=1, day=1, unit='ms')
            else:
                partitionTimestamp = pandas.Timestamp(year=partitionsAsDate[-1].year, month=partitionsAsDate[-1].month + 1, day=1, unit='ms')
            partitionsAsDate.append(partitionTimestamp.date())
            partitionsAsTs.append(int(partitionTimestamp.timestamp()*1000))
        return partitionsAsTs

    def getDataFrame(self, start_time, end_time, npartitions=10):
        """
        Query device data and return as a pivoted Pandas DataFrame.

        Reads all metric keys for the device over the time range, then
        pivots the result so that rows are timestamps and columns are
        metric keys.

        Parameters
        ----------
        start_time : str or int
            Start of the time range.
        end_time : str or int
            End of the time range.
        npartitions : int, optional
            Number of parallel partitions. Defaults to 10.

        Returns
        -------
        pandas.DataFrame
            A pivoted DataFrame with timestamps as the index, metric
            keys as columns, and ``dbl_v`` (double) as values.
        """
        bag = self.bag(start_time=start_time, end_time=end_time, npartitions=npartitions)
        df = bag.to_dataframe(meta={'ts': int, 'key': str, 'dbl_v': float})
        df = df.compute().pivot_table(index='ts',columns='key',values='dbl_v')
        return df
