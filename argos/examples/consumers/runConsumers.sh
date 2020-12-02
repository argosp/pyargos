# Note that this is an old version. Use it if you want to run with external configuration file. (The most recent way to run consumers is through the argos-experiment.py)
# The old experiment configuration file example can be found in this directory as experimentConfiguration.json

python argos-kafka-consumers.py --config {The consumers configuration file} --kafkaHost {ip of the kafka host} --projectName {The project name} --expConf {The old experiment configuration file}