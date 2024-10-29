import json
import logging
from argos.experimentSetup.dataObjectsFactory import fileExperimentFactory

# choose experiment
# experimentDirectory = 'argos/experimentSetup/example_exp/exp_simple'
experimentDirectory = 'argos/experimentSetup/example_exp/exp_groups'

# analyze it
fact = fileExperimentFactory(experimentDirectory)
fact.logger.setLevel('DEBUG')
fact.logger.addHandler(logging.StreamHandler())
exp = fact.getExperiment()

# printing
for e in exp.__dict__:
    try:
        s = json.dumps(exp.__dict__[e], indent=2)     
    except:
        s = str(exp.__dict__[e])
    print(e, ':\t', s, '\n')
