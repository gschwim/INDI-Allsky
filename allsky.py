from time import sleep
# from indiclient import IndiClient
import PyIndi
import sys
import threading
import CONFIG

class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
    def newDevice(self, d):
        pass
    def newProperty(self, p):
        pass
    def removeProperty(self, p):
        pass
    def newBLOB(self, bp):
        global blobEvent
        print("new BLOB ", bp.name)
        blobEvent.set()
        pass
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        pass
    def newText(self, tvp):
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        pass
    def serverConnected(self):
        pass
    def serverDisconnected(self, code):
        pass


if __name__ == '__main__':

    indiclient = IndiClient()

    indiclient.setServer('localhost', 7624)

    # print('Server connected: {}'.format(c.connectServer()))
    if not indiclient.connectServer():
        print('No indiserver found at {}:{}'.format(indiclient.getHost(), indiclient.getPort()))
        sys.exit(1)

    sleep(1)

    # get the CCD
    ccd = CONFIG.CCD
    device_ccd = indiclient.getDevice(ccd)

    # connect
    ccd_connect = device_ccd.getSwitch('CONNECTION')
    ccd_connect[0].s = PyIndi.ISS_ON
    ccd_connect[1].s = PyIndi.ISS_OFF
    indiclient.sendNewSwitch(ccd_connect)

    # exposure set up
    ccd_exposure = device_ccd.getNumber('CCD_EXPOSURE')

    ccd_active_devices = device_ccd.getText('ACTIVE_DEVICES')
    # left out telescope sim things here

    indiclient.setBLOBMode(PyIndi.B_ALSO, ccd, 'CCD1')

    ccd_ccd1 = device_ccd.getBLOB('CCD1')

    exposures = [0.0001, 0.0001]

    blobEvent = threading.Event()
    blobEvent.clear()
    i = 0

    ccd_exposure[0].value=exposures[i]

    # This must trigger the exposure
    indiclient.sendNewNumber(ccd_exposure)


    print('1st exposure done. Moving to next....')

    while(i < len(exposures)):
        blobEvent.wait()
        if (i + 1 < len(exposures)):
            ccd_exposure[0].value = exposures[i+1]
            blobEvent.clear()
            indiclient.sendNewNumber(ccd_exposure)

        for blob in ccd_ccd1:
            print('name: {}     size: {}    format: {}'.format(blob.name, blob.size, blob.format))

            fits = blob.getblobdata()
            print('fits data type: {}'.format(type(fits)))

        i += 1