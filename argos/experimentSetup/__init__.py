from .dataObjectsFactory import fileExperimentFactory,webExperimentFactory

WEB = "web"
FILE = "json"


def getExperimentSetup(experimentType, **kwargs):
    """
        Initializes a new experiemnt setup according to the type.

        kwargs contains the parameters that are needed for datalayer.

    :return:
        An experiment object.

    """
    if experimentType not in [WEB, FILE]:
        raise ValueError(f"experimentType must be {FILE} or {WEB}. Got {experimentType}")

    if experimentType==WEB:

        experiment = webExperimentFactory(url=kwargs['url'],token=kwargs['token']).getExperiment(kwargs['experimentName'])

    else:
        experiment= fileExperimentFactory(**kwargs)

    return experiment
