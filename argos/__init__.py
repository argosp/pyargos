__version__ = '0.0.2'

# from argos.old.reports.report import abstractReport,andClause
from .experimentManagement import ExperimentJSON, ExperimentGQL
from .thingsboard.tbHome import tbHome
from .argosWeb import GQLDataLayer


"""
Version 0.0.2
-------------

* switched to the new swagger wrapping. 

getAttributes still doesnt work. 

Version 0.0.1
--------------

* Addition/removal of devices and assets.
* Updating attributes. 
* adding relations. 

TODO: We need to update the tb_api_client and then simplify some of the code 
and allow for further functionality. 

 



"""

# def getJSON():
#     return {
#         'deviceType1': const1
#     }