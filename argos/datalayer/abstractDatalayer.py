import json
import os

class abstractDatalayerFactory:
    """
    The structure of a configuration file:

    {
      "experimentName": "NTA",
      "thingsboard": {
        "login": {
          "username": "...",
          "password": "..."
        },
        "server": {
          "ip": "127.0.0.1",
          "port": "8080"
        }
      },

    }

    """

    _configuration = None

    @property
    def experimentName(self):
        return self._configuration['experimentName']

    @property
    def experimentConfiguration(self):
        return self._configuration

    @property
    def thingsboardConfiguration(self):
        return self._configuration['thingsboard']


    def __init__(self,experimentConfiguration):
        """
            Initializes the absrtact factory.

        :param experimentConfiguration: str, json
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


