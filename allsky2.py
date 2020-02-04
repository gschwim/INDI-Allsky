import sys, time, logging
import PyIndi
from astropy.io import fits
import numpy as np
from time import sleep
  
class IndiClient(PyIndi.BaseClient):
 
	device = None
 
	def __init__(self):
		super(IndiClient, self).__init__()
		self.logger = logging.getLogger('PyQtIndi.IndiClient')
		# self.logger.info('creating an instance of PyQtIndi.IndiClient')

		self.exptime = 0.000064 # start low and go up
	def newDevice(self, d):
		# self.logger.info("new device " + d.getDeviceName())
		if 'CCD' in d.getDeviceName():
			# self.logger.info("Set new device CCD!")
			# save reference to the device in member variable
			self.device = d
	def newProperty(self, p):
		# self.logger.info("new property "+ p.getName() + " for device "+ p.getDeviceName())
		if self.device is not None and p.getName() == "CONNECTION" and p.getDeviceName() == self.device.getDeviceName():
			# self.logger.info("Got property CONNECTION for CCD Simulator!")
			# connect to device
			self.connectDevice(self.device.getDeviceName())
			# set BLOB mode to BLOB_ALSO
			self.setBLOBMode(1, self.device.getDeviceName(), None)
		if p.getName() == "CCD_EXPOSURE":
			# take first exposure
			self.takeExposure()
	def removeProperty(self, p):
		# self.logger.info("remove property "+ p.getName() + " for device "+ p.getDeviceName())
		pass
	def newBLOB(self, bp):
		self.logger.info("new BLOB "+ bp.name)
		# get image data
		img = bp.getblobdata()
		# write image data to BytesIO buffer
		import io
		blobfile = io.BytesIO(img)
		# open a file and save buffer to disk
		with open("frame.fit", "wb") as f:
			f.write(blobfile.getvalue())

		# process image for consumption
		self.processImage(blobfile)
		# start new exposure
		self.takeExposure()

	def newSwitch(self, svp):
		pass
	# self.logger.info ("new Switch "+ svp.name + " for device "+ svp.device)
	def newNumber(self, nvp):
		pass
		# self.logger.info("new Number "+ nvp.name + " for device "+ nvp.device)
	def newText(self, tvp):
		pass
	# self.logger.info("new Text "+ tvp.name + " for device "+ tvp.device)
	def newLight(self, lvp):
		pass
	# self.logger.info("new Light "+ lvp.name + " for device "+ lvp.device)
	def newMessage(self, d, m):
		#self.logger.info("new Message "+ d.messageQueue(m))
		pass
	def serverConnected(self):
		self.logger.infi("Server connected ("+self.getHost()+":"+str(self.getPort())+")")
	def serverDisconnected(self, code):
		self.logger.info("Server disconnected (exit code = "+str(code)+","+str(self.getHost())+":"+str(self.getPort())+")")
	def takeExposure(self):
		self.logger.info(">>>>>>>>")
		#get current exposure time
		exp = self.device.getNumber("CCD_EXPOSURE")
		# set exposure time to 5 seconds
		# etime = 1.0
		exp[0].value = self.exptime
		# send new exposure time to server/device
		self.logger.info('Exposing: {}'.format(self.exptime))
		self.sendNewNumber(exp)
		# print('Sleeping {}'.format(etime + 10))
		# time.sleep(etime+10)
	def processImage(self, blobfile):

		# turn blob into an astropy.io.fits object
		fit = fits.open(blobfile)
		img = fit[0].data.T
		headers = fit[0].header

		# get the exposure time
		exptime = headers['EXPTIME']
		self.logger.info('Exposure time found: {}'.format(exptime))

		# get the median of the image
		imgMedian = np.median(img)
		self.logger.info('Image median: {}'.format(imgMedian))

		newExptime = 1100 / (imgMedian / self.exptime)

		if newExptime < 0.000064:
			newExptime = 0.000064
		
		self.exptime = newExptime

		f = open('log.txt', 'a+')
		log = '{},{},{}\n'.format(exptime, self.exptime, imgMedian)
		f.write(log)
		f.close()



if __name__ == '__main__':

	logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
	 
	# instantiate the client
	indiclient=IndiClient()
	# set indi server localhost and port 7624
	indiclient.setServer("localhost",7624)
	# connect to indi server
	print("Connecting to indiserver")
	if (not(indiclient.connectServer())):
		 print("No indiserver running on "+indiclient.getHost()+":"+str(indiclient.getPort())+" - Try to run")
		 print("  indiserver indi_simulator_telescope indi_simulator_ccd")
		 sys.exit(1)

	sleep(indiclient.exptime + 3) 
	# indiclient.disconnectServer()
	# start endless loop, client works asynchron in background
	#while True:
	#    time.sleep(10)
	
