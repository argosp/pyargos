__version__ = '0.1.0'

# from argos.old.reports.report import abstractReport,andClause
#from .manager import ExperimentJSON, ExperimentGQL
#from .thingsboard.tbHome import tbHome
from .datalayer.argosWebDatalayer import GQLDataLayerFactory


"""
Version 0.1.0
-------------
* Added graphQL interface
* Started using kafka consumers(processors)

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

# ---------------- to do -----------------------------
# from hera import METEOROLOGICAL, DISPERSION, ...
# deviceTypeToDocTypeDict = dict(Raw_Sonic=METEOROLOGICAL,
#                                NDIR=DISPERSION,
#                                .
#                                .
#                                .
#                                )