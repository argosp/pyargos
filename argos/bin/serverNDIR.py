"""
    Todo:
    -----
    1. change name to serverNDIR.
    2. Read all the devices and fileter only NDIR
    3. Create the clients for the NDIR (get credential).

    4. Make a run.sh file with the execution of : spark and server.

    5. Test (and test with writing from a remote computer).
    
    [Future]
    5. Add logs.



"""
import errno
import functools
import socket
from time import sleep
import pandas
import paho.mqtt.client as mqtt
import json
from argos import tbHome

import tornado.ioloop
from tornado.iostream import IOStream
from multiprocessing.pool import ThreadPool

_workers = ThreadPool(50)

thingsboardHost = "127.0.0.1"

connectionMap = {}


def on_disconnect(client, userdata, rc=0):
    logging.debug("DisConnected result code " + str(rc))
    client.loop_stop()


# blocking task like querying to MySQL
def blocking_task(msg):
    """
	Parsing the message of Amnon: 

	ID,xloc,yloc,dd,mm,yyyy,hh,mm,ss,v2000,v50,ppm2000,ppm50
    """
    msg = msg.decode("utf-8")
    fields = ["deviceName", "longitude", "latitude", "day", "month", "year", "hour", "minute", "second", "v2000", "v50",
              "ppm2000", "ppm50"]
    msgMap = dict([x for x in zip(fields, msg.split(","))])

    dateFrmt = pandas.Timestamp("{month}/{day}/{year} {hour}:{minute}:{second}".format(**msgMap)).tz_localize("Israel")

    newMap = {}
    for field in ["longitude", "latitude", "v2000", "v50", "ppm2000", "ppm50"]:
        newMap[field] = float(msgMap[field])


    # print(dateFrmt)
    # strdata = "{'ts' : %s,'values' : %s}" % (int(dateFrmt.timestamp()*1000),str(newMap))
    strdata = "{'ts' : %s,'values' : %s}" % (int(dateFrmt.timestamp()*1000),str(newMap))
    myClient = connectionMap[msgMap["deviceName"]]
    myClient.publish('v1/devices/me/telemetry', strdata)


async def handle_connection(connection, address):
    stream = IOStream(connection)
    while 1:
        try:
            message = await stream.read_until(b"\n")
        except:
            print("bye")
            return
        _workers.apply_async(blocking_task, args=(message,), kwds={})
        # print("message from client:", message.decode().strip())


def connection_ready(sock, fd, events):
    while True:
        try:
            connection, address = sock.accept()
        except socket.error as e:
            if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            return
        connection.setblocking(0)
        io_loop = tornado.ioloop.IOLoop.current()
        io_loop.spawn_callback(handle_connection, connection, address)


if __name__ == '__main__':
    ## Test
    with open('/home/yehudaa/Projects/2019/DesertWalls/experimentConfiguration.json') as credentialOpen:
        credentialMap = json.load(credentialOpen)
    tbh = tbHome(credentialMap["connection"])

    devicesNames = tbh.deviceHome.getAllEntitiesNameByType('NDIR')

    for deviceName in devicesNames: # [x for x in devicesNames if (x["Type"] =="NDIR")]: ## change to
        client = mqtt.Client("Me_%s" % deviceName)
        # getting accessToken.
        # for this demo - accessToken = ID.
        accessToken = tbh.deviceHome.createProxy(deviceName).getCredentials()
        client.username_pw_set(accessToken, password=None)
        client.on_disconnect = on_disconnect
        client.connect(thingsboardHost)
        client.loop_start()
        connectionMap[deviceName] = client

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind(("", 5000))
    sock.listen(128)

    io_loop = tornado.ioloop.IOLoop.current()
    callback = functools.partial(connection_ready, sock)
    io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
    io_loop.start()
