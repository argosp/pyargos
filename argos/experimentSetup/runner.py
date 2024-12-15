import json
import logging
import sys
from argos.experimentSetup.dataObjectsFactory import fileExperimentFactory
from argos.utils.logging.helpers import unify_all_logs_debug
from ..utils.logging import get_logger as argos_get_logger

# choose experiment
# experimentDirectory = 'argos/experimentSetup/example_exp/exp_simple'
experimentDirectory = 'argos/experimentSetup/example_exp/exp_groups'
unify_all_logs_debug()
logger = argos_get_logger("")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.info(f"Hello runner!")

# analyze it
fact = fileExperimentFactory(experimentDirectory)
exp = fact.getExperiment()

# printing
# for e in exp.__dict__:
#     try:
#         s = json.dumps(exp.__dict__[e], indent=2)     
#     except:
#         s = str(exp.__dict__[e])
#     print(e, ':\t', s, '\n')

# print(json.dumps(
#     exp.trialSet['New Trial Type']['New Trial']._metadata['entities']
# , indent=2))

devOnTrial = exp.trialSet['New Trial Type']['New Trial'].designEntitiesTable
js = devOnTrial.to_json(orient='records')
print(json.dumps(json.loads(js), indent=2))
