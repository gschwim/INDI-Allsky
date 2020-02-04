
import PyIndi

# class IndiClient(PyIndi.BaseClient):
#     def __init__(self):
#         super(IndiClient, self).__init__()
#         self.logger = logging.getLogger('IndiClient')
#         self.logger.info('creating an instance of IndiClient')
#     def newDevice(self, d):
#         self.logger.info("new device " + d.getDeviceName())
#     def newProperty(self, p):
#         self.logger.info("new property "+ p.getName() + " for device "+ p.getDeviceName())
#     def removeProperty(self, p):
#         self.logger.info("remove property "+ p.getName() + " for device "+ p.getDeviceName())
#     def newBLOB(self, bp):
#         # self.logger.info("new BLOB "+ bp.name.decode())
#         pass
#     def newSwitch(self, svp):
#         # self.logger.info ("new Switch "+ svp.name.decode() + " for device "+ svp.device.decode())
#         pass
#     def newNumber(self, nvp):
#         # self.logger.info("new Number "+ nvp.name.decode() + " for device "+ nvp.device.decode())
#         pass
#     def newText(self, tvp):
#         # self.logger.info("new Text "+ tvp.name.decode() + " for device "+ tvp.device.decode())
#         pass
#     def newLight(self, lvp):
#         # self.logger.info("new Light "+ lvp.name.decode() + " for device "+ lvp.device.decode())
#         pass
#     def newMessage(self, d, m):
#         self.logger.info("new Message "+ d.messageQueue(m))
#     def serverConnected(self):
#         self.logger.info("Server connected ("+self.getHost()+":"+str(self.getPort())+")")
#     def serverDisconnected(self, code):
#         self.logger.info("Server disconnected (exit code = "+str(code)+","+str(self.getHost())+":"+str(self.getPort())+")")


class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
    def newDevice(self, d):
        pass
    def newProperty(self, p):
        print('PROPERTY: {}'.format(p.getName()))
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