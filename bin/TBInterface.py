"""
    This class gets a list of actions and executes them on the TB server.

    For simplicity I have implemented it with JSON file, but I guess it should be
    simple to implement other interfaces.

    Json structure:

    {
        "actions" : [<list of actions>]
    }

    Currently, there are 2 action:

*   Add entity (device/asset):
    --------------------------

    {
        "action" : "addEntity",
        "type"   : "device|asset",
        "name"   : <name>,
        "type"   : <the type>
    }
    prints error if the entity exists and type != stored type.

*    Update attributes
     ----------------------------
     {
        "action" : "updateAttributes"
     }


"""
import json
import argparse
import pyargos.thingsboard as tb

parser = argparse.ArgumentParser()
parser.add_argument("--connection",dest="conf" ,help="The connection file",required=True)
parser.add_argument("--actions",dest="jsonfile" ,help="A JSON with the actions",required=True)
args = parser.parse_args()

with open(args.jsonfile,"r") as infile:
    actions = json.load(infile)

with open(args.conf,"r") as conffile:
    connection = json.load(conffile)

#connection = {"login": {"username":"tenant@thingsboard.org","password":"tenant"},"server" : {"ip" : "192.168.11.203","port":"8080"}}

home = tb.tbHome(connectdata=connection)

for actionJSON in actions["actions"]:
    home.executeAction(actionJSON)
