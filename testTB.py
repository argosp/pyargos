import pyargos.thingsboard as tb

if __name__=="__main__":
    connection = {"login": {"username":"tenant@thingsboard.org","password":"tenant"},"server" : {"ip" : "192.168.11.203","port":"8080"}}

    home = tb.tbHome(connectdata=connection)
    #print(home.deviceHome.exists("Device"))
    #print(home.deviceHome.exists("device"))

    home.deviceHome.createProxy("Device","RawSonic")