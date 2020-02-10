from time import sleep
from indiclient import IndiClient
import PyIndi


def strISState(s):
    if (s == PyIndi.ISS_OFF):
        return "Off"
    else:
        return "On"
def strIPState(s):
    if (s == PyIndi.IPS_IDLE):
        return "Idle"
    elif (s == PyIndi.IPS_OK):
        return "Ok"
    elif (s == PyIndi.IPS_BUSY):
        return "Busy"
    elif (s == PyIndi.IPS_ALERT):
        return "Alert"



indiclient = IndiClient()

indiclient.setServer('localhost', 7624)

# print('Server connected: {}'.format(c.connectServer()))
if not indiclient.connectServer():
    print('No indiserver found at {}:{}'.format(indiclient.getHost(), indiclient.getPort()))
    sys.exit(1)

sleep(1)


dlist = indiclient.getDevices()

for dev in dlist:
    print(dev.getDeviceName())

###
    # Print all properties and their associated values.
print("List of Device Properties")
for d in dlist:
    print("-- " + d.getDeviceName())
    lp = d.getProperties()
    for p in lp:
        print("   > " + p.getName())
        if p.getType() == PyIndi.INDI_TEXT:
            tpy = p.getText()
            for t in tpy:
                print("TEXT:       " + t.name + "(" + t.label + ")= " + t.text)
        elif p.getType()==PyIndi.INDI_NUMBER:
            tpy=p.getNumber()
            for t in tpy:
                print("NUMBER:       "+t.name+"("+t.label+")= "+str(t.value))
        elif p.getType()==PyIndi.INDI_SWITCH:
            tpy=p.getSwitch()
            for t in tpy:
                print("SWITCH:       "+t.name+"("+t.label+")= "+strISState(t.s))
        elif p.getType()==PyIndi.INDI_LIGHT:
            tpy=p.getLight()
            for t in tpy:
                print("LIGHT:       "+t.name+"("+t.label+")= "+strIPState(t.s))
        elif p.getType()==PyIndi.INDI_BLOB:
            tpy=p.getBLOB()
            for t in tpy:
                print("BLOB:       "+t.name+"("+t.label+")= <blob "+str(t.size)+" bytes>")

# Disconnect from the indiserver
# print("Disconnecting")
# c.disconnectServer()