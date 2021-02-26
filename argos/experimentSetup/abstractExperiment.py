import json
import os

class abstractDatalayer:
    """

        Abstract experimentSetup.

        Holds the configuration and allows either string, file or dict configuration
        as input.

        The structure of the configuration
    """

    _configuration = None

    @property
    def experimentConfiguration(self):
        return self._configuration

    @property
    def thingsboardConfiguration(self):
        return self._configuration['thingsboard']


    def __init__(self,experimentConfiguration):
        """
            Initializes the abstract factory with the configuration file.

        Parameters
        ----------
        experimentConfiguration: str, json
                Either filename or JSON string or a json object.
        """
        if isinstance(experimentConfiguration,str):
            if os.path.exists(experimentConfiguration):
                with open(experimentConfiguration,'r')  as inputFile:
                    self._configuration = json.load(inputFile)
            else:
                try:
                    self._configuration = json.load(experimentConfiguration)
                except json.JSONDecodeError:
                    raise ValueError("input must be a JSON file, JSON string or a JSON object")

        else:
            self._configuration = experimentConfiguration


