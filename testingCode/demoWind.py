import sys
import paho.mqtt.client as mqtt
import numpy 
from numpy import random
import time
import argparse
import pandas
import json
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')))

from pyargos.thingsboard.tbHome import tbHome

def on_connect(client, userdata, flags, rc):

    if rc == 0:

        print("Connected to broker")

    else:

        print("Connection failed")


parser = argparse.ArgumentParser()
parser.add_argument("--deviceName",dest="name", help="The device name",required=True)
#parser.add_argument("--dataAmount",dest="amount", help="The amount of data per delay time",required=True, type=int)
parser.add_argument("--period",dest="period", help="Send a msg every period time (seconds)",required=True, type=int)
#parser.add_argument("--totalTime",dest="time", help="The total time in seconds",required=True, type=int)
args = parser.parse_args()


with open('experimentConfiguration.json', 'r') as expConf:
    config = json.load(expConf)
tbh = tbHome(config['connection'])

accessToken = tbh._deviceHome.createProxy(args.name).getCredentials()

min_wind_dir = 0
max_wind_dir = 360
min_wind_speed = 0
max_wind_speed = 10

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

client.loop_start()
while (True):
    data={}  
    data["ts"] = int(pandas.datetime.now().timestamp()*1000)
    data['wind_dir']   = max_wind_dir   * random.rand()
    data['wind_speed'] = max_wind_speed * random.rand()

    print("Published %s" % str(data))
    client.publish('v1/devices/me/telemetry',str(dict(data)))
    time.sleep(args.period)

client.loop_stop()
client.disconnect()
