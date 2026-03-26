"""
Experiment setup module for pyArgos.

Provides factory classes and data objects for loading and working with
Argos experiment configurations from local files or the ArgosWEB server.

Constants
---------
WEB : str
    Source type for web-based experiments (``"web"``).
FILE : str
    Source type for file-based experiments (``"json"``).
"""

from .dataObjectsFactory import fileExperimentFactory,webExperimentFactory

WEB = "web"
FILE = "json"



def getExperimentSetup(experimentType,experimentName, **kwargs):
    """
    Load an experiment using the appropriate factory based on source type.

    A convenience function that routes to either ``fileExperimentFactory``
    or ``webExperimentFactory`` depending on the ``experimentType`` parameter.

    Parameters
    ----------
    experimentType : str
        The source type: ``"web"`` for ArgosWEB or ``"json"`` for local files.
        Use the module constants ``WEB`` and ``FILE``.
    experimentName : str
        The name of the experiment to load.
    **kwargs : dict
        Additional keyword arguments passed to the factory:

        - For ``WEB``: ``url`` (str) and ``token`` (str) are required.
        - For ``FILE``: ``experimentPath`` (str, optional) specifies the directory.

    Returns
    -------
    Experiment
        The loaded experiment object.

    Raises
    ------
    ValueError
        If ``experimentType`` is not ``WEB`` or ``FILE``.

    Examples
    --------
    >>> from argos.experimentSetup import getExperimentSetup, FILE, WEB
    >>> experiment = getExperimentSetup(FILE, "MyExp", experimentPath="/path/to/exp")
    >>> experiment = getExperimentSetup(WEB, "MyExp", url="http://server", token="abc")
    """
    if experimentType not in [WEB, FILE]:
        raise ValueError(f"experimentType must be {FILE} or {WEB}. Got {experimentType}")

    if experimentType==WEB:
        experiment = webExperimentFactory(url=kwargs['url'],token=kwargs['token'])
    else:
        experiment= fileExperimentFactory(**kwargs)

    return experiment.getExperiment(experimentName)
