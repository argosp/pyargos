import dask
import pymongo
import pandas

class MongoBag:

    _db_name = None
    _collection_name = None

    _timestamp_field = None

    @property
    def db_name(self):
        return self._db_name

    @property
    def collection_name(self):
        return self._collection_name

    @property
    def timestamp_field(self):
        return self._timestamp_field

    def __init__(self,db_name, collection_name,datetimeField="timestamp"):
        self._db_name = db_name
        self._collection_name = collection_name
        self._timestamp_field  = datetimeField

    def bag(self, start_time, end_time, periods: int = 10 ,freq : str =None,**qry):

        start_time = pandas.to_datetime(start_time)
        end_time   = pandas.to_datetime(end_time)

        dateRange = pandas.date_range(start_time,end_time,periods=periods,freq=freq,tz="israel")

        partitions_requests = list(zip(dateRange[:-1], dateRange[1:]))
        b = (dask.bag.from_sequence(partitions_requests)
             .map(lambda x: self.read_datetime_interval_from_collection(x,**qry))
             .flatten())
        return b

    def read_datetime_interval_from_collection(self, args,**qry):

        start_ts = args[0].strftime("%Y-%-m-%-d %-H:%-M:%-S.%f")
        end_ts   = args[1].strftime("%Y-%-m-%-d %-H:%-M:%-S.%f")

        full_qry = {self._timestamp_field: {'$gte': start_ts, '$lte': end_ts}}
        full_qry.update(qry)

        with pymongo.MongoClient() as mongo_client:
            collection = mongo_client[self.db_name][self.collection_name]
            items = list(collection.find(full_qry))
        return items

    def debug_read_datetime_interval_from_collection(self, args,**qry):

        start_ts = args[0]
        end_ts   = args[1]

        full_qry = {self._timestamp_field: {'$gte': start_ts, '$lte': end_ts}}
        # full_qry.update(qry)

        with pymongo.MongoClient() as mongo_client:
            collection = mongo_client[self.db_name][self.collection_name]
            items = list(collection.find(full_qry))
        return items



