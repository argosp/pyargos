Loading trial to Thingsboard.
*****************************

1. Goto the experiment main directory.
2. Run the script

::
    trialManager --expConf [path to experiment configuration file]  --load [trial name]

The code searches for the experimentData/Trials/execution directory for the file [trial name].json.
if not found, tries to copy it from the experimentData/Trials/design
and the load it to the Thingboard.



