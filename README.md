# pyargos
Python wrappings for the argos project

## Install 
==========

- Install anaconda python 3.7 
- Add the pyargos to the PYTHONPATH 


## Loading a trial using the CLI
===================================

1. You need to make a directory like ExpExample (it will be your experiment directory).

2. In ExpExample you can find experimentConfiguration.json which configures the thingsboard you work on(IP, port and account information).
   Change it to your configurations.

3. In ExpExampe/experimentData you can find ExperimentData.json which contains the information about the entities(devices/assets) you want to create.
   The "properties"/"claculationWindows" part is irrelevant for you and you can leave it empty(delete all the items under "calculationWindows"). (It creates another "window" devices of each type specified, with a name "{deviceName}_{window}s' for each window specified).
   Under "Entities" you specify the etities you want to create.
   "entityType": The entity type ("DEVICE" or "ASSET")
   "Number": How many entities like this you want. (*In the "nameFormat" key you have {id}, that will run from 1 to the Number value)
   "Type": The type of the device/asset.
   "nameFormat": The format of the name. (For example, if Number=3 and namFormat="name_{id:02d}", you will get 3 devices with names: "name_01", "name_02", "name_03")

4. Now after you done all the configurations, you are ready to setup the experiment.
   Setup your current directory as ExpExample(you must be under an experiment directory)
   You setup with this line: 
   ```
   python yourpath/pyargos/bin/trialManager.py --expConfig experimentConfiguration.json --setup
   ```
   Where "yourpath" is the path to the directory which contains pyargos. 
   This creates a json file, which called "trialTemplate.json", under ExpExample/experimentData/trials.

5. Copy the trialTemplate.json to the ExpExample/experimentData/trials/design directory.
   The name of the file will be the name of the trial. 
   Now edit trialTemplate.json to add the attributes and relations that are related to the trial. 
   
   You can edit for each entity the "Name"/ "Type"/ "attributes"/ "entityType"/ "contains"(*Under "contains" you have a list of lists like [entityType, entityName] which set a relation of type "Contains" from your current entity to the entities in the list)

6. Upload the trial to thingsboard.
   ```
    python yourpath/pyargos/bin/trialManager.py --expConfig experimentConfiguration.json --load trialName
   ```
   where trialName is the name of the trial you chose last step.

## Running a demo device 
=========================

Install the [paho package](https://anaconda.org/wheeler-microfluidics/paho-mqtt)

Run the demoDevice from the CLI. 





