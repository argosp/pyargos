import json
import requests



class flowManagerHome:

    _noderedServer = None
    _noderedPort   = None

    def getConnectionString(self,task):
        return f"http://{self._noderedServer}:{self._noderedPort}/{task}"

    def __init__(self,nodeRedServer="127.0.0.1"):
        self._noderedServer  = nodeRedServer
        self._noderedPort    = 1880


    def getFlows(self):

        flowStr = self.getConnectionString("flows")

        resp = requests.get(flowStr)
        if resp.status_code != 200:
            # This means something went wrong.
            raise ValueError(f"GET {flowStr} {resp.status_code}")
        return resp.json()




if __name__=="__main__":
    flowmanager = flowManagerHome()
    res = flowmanager.getFlows()



