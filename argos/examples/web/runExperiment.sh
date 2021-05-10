# Experiment configuration example can be found in this directory as expConf.json

# Experiment setup
python argos-experiment-web.py --expConf {The experiment configuration} --setup

# Trial load
python argos-experiment-web.py --expConf {The experiment configuration} --load {trial set name} {trial name}

# Run consumers
python argos-experiment-web.py --expConf {The experiment configuration} --runConsumers {default folder for saving data}

# Finalize (Updating the database documents desc with the information from the trials)
python argos-exeperiment-web.py --expConf {The experiments configuration} --finalize