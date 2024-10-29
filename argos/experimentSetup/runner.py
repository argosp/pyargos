import json
import logging
from argos.experimentSetup.dataObjectsFactory import fileExperimentFactory

# experimentDirectory = 'argos/experimentSetup/example_exp/exp_simple'
experimentDirectory = 'argos/experimentSetup/example_exp/exp_groups'
fact = fileExperimentFactory(experimentDirectory)
fact.logger.setLevel('DEBUG')
fact.logger.addHandler(logging.StreamHandler())
exp = fact.getExperiment()
for e in exp.__dict__:
    print(e, exp.__dict__[e])
    print()