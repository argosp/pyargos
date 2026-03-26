"""
Dask-based interface to MongoDB time-series collections.

Provides the ``MongoBag`` class for querying time-series data from
MongoDB using Dask for parallel, partitioned reads.
"""

import dask
import pymongo
import pandas

class MongoBag:
    """
    Dask bag interface for querying MongoDB time-series collections.

    Partitions a time range into intervals and reads each interval in
    parallel using Dask bags.

    Parameters
    ----------
    db_name : str
        The MongoDB database name.
    collection_name : str
        The collection name within the database.
    datetimeField : str, optional
        The name of the timestamp field in the documents.
        Defaults to ``"timestamp"``.

    Examples
    --------
    >>> bag = MongoBag(db_name="mydb", collection_name="sensor_data")
    >>> dask_bag = bag.bag("2024-01-01", "2024-01-31", periods=20)
    >>> df = dask_bag.to_dataframe().compute()
    """

    _db_name = None
    _collection_name = None

    _timestamp_field = None

    @property
    def db_name(self):
        """
        The MongoDB database name.

        Returns
        -------
        str
            The database name.
        """
        return self._db_name

    @property
    def collection_name(self):
        """
        The MongoDB collection name.

        Returns
        -------
        str
            The collection name.
        """
        return self._collection_name

    @property
    def timestamp_field(self):
        """
        The name of the timestamp field used for time-range queries.

        Returns
        -------
        str
            The timestamp field name.
        """
        return self._timestamp_field

    def __init__(self,db_name, collection_name,datetimeField="timestamp"):
        """
        Initialize the MongoBag.

        Parameters
        ----------
        db_name : str
            The MongoDB database name.
        collection_name : str
            The collection name.
        datetimeField : str, optional
            The timestamp field name. Defaults to ``"timestamp"``.
        """
        self._db_name = db_name
        self._collection_name = collection_name
        self._timestamp_field  = datetimeField

    def bag(self, start_time, end_time, periods: int = 10 ,freq : str =None,**qry):
        """
        Create a Dask bag for parallel reads over a time range.

        Splits the time range into partitions using ``pandas.date_range``
        and reads each partition in parallel.

        Parameters
        ----------
        start_time : str
            Start of the time range (parsed by ``pandas.to_datetime``).
        end_time : str
            End of the time range.
        periods : int, optional
            Number of partitions. Defaults to 10. Ignored if ``freq`` is set.
        freq : str, optional
            Partition frequency (e.g., ``"1D"``, ``"1H"``). If set,
            ``periods`` is ignored.
        **qry : dict
            Additional MongoDB query filters merged into each partition's
            query.

        Returns
        -------
        dask.bag.Bag
            A Dask bag of document dicts from the collection.
        """

        start_time = pandas.to_datetime(start_time)
        end_time   = pandas.to_datetime(end_time)

        dateRange = pandas.date_range(start_time,end_time,periods=periods,freq=freq,tz="israel")

        partitions_requests = list(zip(dateRange[:-1], dateRange[1:]))
        b = (dask.bag.from_sequence(partitions_requests)
             .map(lambda x: self.read_datetime_interval_from_collection(x,**qry))
             .flatten())
        return b

    def read_datetime_interval_from_collection(self, args,**qry):
        """
        Read documents from MongoDB for a single time interval.

        Parameters
        ----------
        args : tuple[Timestamp, Timestamp]
            A ``(start, end)`` tuple of partition boundaries.
        **qry : dict
            Additional MongoDB query filters.

        Returns
        -------
        list[dict]
            A list of document dicts matching the time range and filters.
        """

        start_ts = args[0].strftime("%Y-%-m-%-d %-H:%-M:%-S.%f")
        end_ts   = args[1].strftime("%Y-%-m-%-d %-H:%-M:%-S.%f")

        full_qry = {self._timestamp_field: {'$gte': start_ts, '$lte': end_ts}}
        full_qry.update(qry)

        with pymongo.MongoClient() as mongo_client:
            collection = mongo_client[self.db_name][self.collection_name]
            items = list(collection.find(full_qry))
        return items
