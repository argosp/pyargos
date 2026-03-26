"""
Node-RED flow manager REST interface.

Provides a simple HTTP client for interacting with a Node-RED server's
REST API to retrieve and manage flows.
"""

import json
import requests



class flowManagerHome:
    """
    REST client for a Node-RED server.

    Connects to a Node-RED instance and provides methods to query
    the server's flow definitions.

    Parameters
    ----------
    nodeRedServer : str, optional
        The hostname or IP of the Node-RED server. Defaults to ``"127.0.0.1"``.

    Examples
    --------
    >>> manager = flowManagerHome("192.168.1.10")
    >>> flows = manager.getFlows()
    """

    _noderedServer = None
    _noderedPort   = None

    def getConnectionString(self,task):
        """
        Build the full URL for a Node-RED REST endpoint.

        Parameters
        ----------
        task : str
            The endpoint path (e.g., ``"flows"``, ``"nodes"``).

        Returns
        -------
        str
            The full URL string (e.g., ``"http://127.0.0.1:1880/flows"``).
        """
        return f"http://{self._noderedServer}:{self._noderedPort}/{task}"

    def __init__(self,nodeRedServer="127.0.0.1"):
        """
        Initialize the flow manager.

        Parameters
        ----------
        nodeRedServer : str, optional
            The hostname or IP of the Node-RED server. Defaults to ``"127.0.0.1"``.
        """
        self._noderedServer  = nodeRedServer
        self._noderedPort    = 1880


    def getFlows(self):
        """
        Retrieve all flow definitions from the Node-RED server.

        Sends a GET request to the ``/flows`` endpoint.

        Returns
        -------
        dict
            The JSON response containing all flow definitions.

        Raises
        ------
        ValueError
            If the server returns a non-200 HTTP status code.
        """

        flowStr = self.getConnectionString("flows")

        resp = requests.get(flowStr)
        if resp.status_code != 200:
            # This means something went wrong.
            raise ValueError(f"GET {flowStr} {resp.status_code}")
        return resp.json()



if __name__=="__main__":
    flowmanager = flowManagerHome()
    res = flowmanager.getFlows()
