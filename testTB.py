import pyargos.thingsboard as tb

if __name__=="__main__":
    connection = {"login": {"username":"tenant@thingsboard.org","password":"tenant"},"server" : {"ip" : "192.168.11.203","port":"8080"}}

    home = tb.tbHome(connectdata=connection)
