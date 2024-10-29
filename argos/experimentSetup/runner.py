import logging
from argos.experimentSetup.dataObjectsFactory import fileExperimentFactory

experimentDirectory = 'argos/experimentSetup/exp/'
fact = fileExperimentFactory(experimentDirectory)
fact.logger.setLevel('INFO')
fact.logger.addHandler(logging.StreamHandler())
fact.getExperiment()
