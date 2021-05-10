# pyargos
Python wrappings for the argos project

## Install 
==========

- Install anaconda 3 with python 3.7
- Create a virtual enviroment. 
  ```
   conda create -n Argos python=3.6.5 
   conda activate Argos 
   pip install paho-mqtt numpy pandas urllib3 requests
  ```
- Add the pyargos to the PYTHONPATH 
- Activate the enviroment before executing 
  ```
    conda activate Argos
  ```


## Loading a trial using the CLI
===================================

1. You need to make a directory like ExpExample (it will be your experiment directory).

2. In ExpExample you can find experimentConfiguration.json which configures the thingsboard you work on(IP, port and account information).
   Change it to your configurations.

3. In ExpExampe/experimentData you can find ExperimentData.json which contains the information about the entities(devices/assets) you want to create.
   - The "properties"/"claculationWindows" part creates another devices of each type specified, with 
   the name "{deviceName}_{window}s" for each window specified. 
   This device is used for the streaming calculations. 
      
   - "Entities":  specify the entities (currently only devices and assets) to create.
   
         - entityType: The entity type ("DEVICE" or "ASSET")
         - "Number": How many entities like this you want. 
         - "Type": The type of the device/asset.
         - "nameFormat": The format of the name. {id} will be replaced by the running number of the device. (start at 1)
         (For example, if Number=3 and namFormat="name_{id:02d}", you will get 3 devices with names: "name_01", "name_02", "name_03")

4. Now after you done all the configurations, you are ready to setup the experiment.
   Setup your current directory as ExpExample(you must be under an experiment directory)
   You setup with this line: 
   ```
   python yourpath/pyargos/bin/trialManager.py --expConf experimentConfiguration.json --setup
   ```
   Where "yourpath" is the path to the directory which contains pyargos. 
   This creates a json file, which called "trialTemplate.json", under ExpExample/experimentData/trials.

5. Copy the trialTemplate.json to the ExpExample/experimentData/trials/design directory.
   The name of the file will be the name of the trial. 
   Now edit trialTemplate.json to add the attributes and relations that are related to the trial. 
   
   You can edit for each entity the "Name"/ "Type"/ "attributes"/ "entityType"/ "contains"(*Under "contains" you have a list of lists like [entityType, entityName] which set a relation of type "Contains" from your current entity to the entities in the list)

6. Upload the trial to thingsboard.
   ```
    python yourpath/pyargos/bin/trialManager.py --expConf experimentConfiguration.json --load trialName
   ```
   where trialName is the name of the trial you chose last step.

## Running a demo device 
=========================

Install the [paho package](https://anaconda.org/wheeler-microfluidics/paho-mqtt) in conda environment.

Run the demoDevice from the CLI. 





