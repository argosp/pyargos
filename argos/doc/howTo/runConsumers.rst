Running kafka consumers
***********************

Run the following script

::
    trialManager --config [consumers config json file] --projectName [The project name]

The consumers config json file should be as follows:

    {
        topic:{
            window:{
                slide:{
                    process path:{
                        input key: input value
                    }
                }
            }
        }
    }

For example, a config file for consumers that listen on topic called "device1" with a time window of 60 seconds.
There is one process with path "argos.kafka.processes.process1" on a 30 seconds sliding window without any inputs,
and there is one process with path "argos.kafka.processes.process2" on a 60 seconds sliding window and one input 'inputKey' with value 'inputValue'

    {
        "device1":{
            "60":{
                "30":{
                    "argos.kafka.processes.process1":{
                    }
                },
                "60":{
                    "argos.kafka.processes.process2":{
                        inputKey: inputValue
                    }
                }
            }
        }
    }

* Note you can add as many devices/windows/slides/processes as you wish.