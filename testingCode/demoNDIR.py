import paho.mqtt.client as mqtt
import numpy 
from numpy import random
import time
import argparse
import pandas
from pyargos.thingsboard.tbHome import tbHome
import json

def on_connect(client, userdata, flags, rc):

    if rc == 0:

        print("Connected to broker")

    else:

        print("Connection failed")


parser = argparse.ArgumentParser()
parser.add_argument("--deviceName",dest="name", help="The device name",required=True)
parser.add_argument("--dataAmount",dest="amount", help="The amount of data per delay time",required=True, type=int)
parser.add_argument("--delayTime",dest="delay", help="The delay time in seconds",required=True, type=int)
parser.add_argument("--totalTime",dest="time", help="The total time in seconds",required=True, type=int)
args = parser.parse_args()

if args.time%args.delay != 0:
    raise ValueError('totalTime must be divided by delayTime')

with open('experimentConfiguration.json', 'r') as expConf:
    config = json.load(expConf)
tbh = tbHome(config['connection'])

accessToken = tbh._deviceHome.createProxy(args.name).getCredentials()

min_v1000 = 0
max_v1000 = 1000
min_v50 = 0
max_v50 = 50
max_ppm1000 = 0
min_ppm1000 = 1000
max_ppm50 = 0
min_ppm50 = 50

# values = {
#     "v1000": min_v1000 + (max_v1000 - min_v1000) * random.rand(),
#     "v50": min_v50 + (max_v50 - min_v50) * random.rand(),
#     "ppm1000": min_ppm1000 + (max_ppm1000 - min_ppm1000) * random.rand(),
#     "ppm50": min_ppm50 + (max_ppm50 - min_ppm50) * random.rand(),
# }
# data ={}
# data['ts'] = 0
# data['values'] = values


print(" Initializing " )
client = mqtt.Client("Me")

print(" Set token" )
client.username_pw_set(accessToken, password=None)
client.on_connect= on_connect
print(" connecting..." )
client.connect(thingsboardHost)

data = {}

timeDelta = pandas.Timedelta('%ds' % args.delay)/args.amount
startDate = pandas.datetime.now()

client.loop_start()
if args.delay>1:
    for j in range(int(args.time/args.delay)):
        L = []
        for i in range(args.amount):
            data["ts"] = int(startDate.timestamp()*1000)
            values = {}
            values['v1000'] = min_v1000 + (max_v1000 - min_v1000) * random.rand()
            values['v50'] = min_v50 + (max_v50 - min_v50) * random.rand()
            values['ppm1000'] = min_ppm1000 + (max_ppm1000 - min_ppm1000) * random.rand()
            values['ppm50'] = min_ppm50 + (max_ppm50 - min_ppm50) * random.rand()
            if values['ppm1000'] > 50:
                values['ppm'] = values['ppm1000']
            else:
                values['ppm'] = values['ppm50']
            data['values']=values
            L.append(dict(data))
            startDate = startDate + timeDelta

        print("Published %s" % str(data))
        client.publish('v1/devices/me/telemetry',str(L))
        time.sleep(args.delay)
else:
    for j in range(int(args.time / args.delay)):
        L = []
        for i in range(args.amount):
            data["ts"] = int(startDate.timestamp() * 1000)
            values = {}
            values['v1000'] = min_v1000 + (max_v1000 - min_v1000) * random.rand()
            values['v50'] = min_v50 + (max_v50 - min_v50) * random.rand()
            values['ppm1000'] = min_ppm1000 + (max_ppm1000 - min_ppm1000) * random.rand()
            values['ppm50'] = min_ppm50 + (max_ppm50 - min_ppm50) * random.rand()
            data['values'] = values
            L.append(dict(data))
            startDate = startDate + timeDelta

        print("Published %s" % str(data))
        client.publish('v1/devices/me/telemetry', str(L))
        time.sleep(args.delay)

client.loop_stop()
client.disconnect()
