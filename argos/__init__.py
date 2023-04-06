__version__ = '1.1.0'
from .experimentSetup import WEB,FILE
from .manager import DESIGN,DEPLOY

from .manager import experimentSetup


"""
- Fixed the dataobject. Parses the type of the object
        Only parses text,number and location. 
        Should expand to datetime, bool and ect. 
        
- Fixed the loading trial: removes old attributes before loading.  
     
- Adding the argos-experiment-manager to setup, and load trials to thingsboard. 

- Fixing the dataObject with the new DB structure. 
   ** still did not add the contains property to the library.

Version 1.1.0
-------------

- Added factory to handle with JSON version 2.0.0 and all experiment data in zip file. 

Version 1.0.0
-------------

- Changes devices->entities

Version 0.4.0
-------------

- Added default assets. (windows and device groups).  
- Loading devices properties for the requested release. 


Version 0.2.0
-------------

* Refactoring the graphQL interface  
* Removed the report 

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
