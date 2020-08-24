import sys, time, logging
import PyIndi
from astropy.io import fits
import numpy as np
from time import sleep
import io
import cv2
import datetime
  
class IndiClient(PyIndi.BaseClient):
 
	device = None
 
	def __init__(self, min_exp=0.000064, max_exp=30.0, gain=30,
				 pacing=30, expose_to=2000, converge_at=0.75,
				 master_bias=None, master_dark=None,
				 resize_pct=100):

		super(IndiClient, self).__init__()
		self.logger = logging.getLogger('PyQtIndi.IndiClient')
		# self.logger.info('creating an instance of PyQtIndi.IndiClient')

		# master frames. Need to add a library capability to this.
		self.logger.info('Calibration Frames - Bias: {} Dark: {}'
						 .format(master_bias, master_dark))
		self.masterBias = master_bias
		self.masterDark = master_dark
		self.masterCalibrator = None
		self.resize_pct = resize_pct


		# min/max exposure times
		self.minExp = min_exp
		self.maxExp = max_exp
		self.startingGain = gain
		self.gain = self.startingGain

		# median background target
		self.exposeTarget = expose_to

		# pacing - how often an image is produced regardless of the exposure length
		self.pacing = pacing

		# TODO - minimum exposure needs to be read from the camera
		self.expTime = self.minExp # start low and go up
		self.expConverged = False
		self.convergeAt = converge_at

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

		if self.device is not None and p.getName() == 'CCD_CONTROLS' and p.getDeviceName() == self.device.getDeviceName():
			sleep(1.0)
			self.setCCDControls()

		if p.getName() == "CCD_EXPOSURE":
			# take first exposure
			self.takeExposure()

	def removeProperty(self, p):
		# self.logger.info("remove property "+ p.getName() + " for device "+ p.getDeviceName())
		pass

	def newBLOB(self, bp):
		# self.logger.info("new BLOB "+ bp.name)
		# get image data
		img = bp.getblobdata()
		# write image data to BytesIO buffer
		# import io
		self.fit = io.BytesIO(img)
		# open a file and save buffer to disk
		with open('/dev/shm/frame.fit', 'wb') as f:
			f.write(self.fit.getvalue())

		# process image for consumption
		self.processImage()
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
		self.logger.info("Server connected ("+self.getHost()+":"+str(self.getPort())+")")

	def serverDisconnected(self, code):
		self.logger.info("Server disconnected (exit code = "
						 +str(code)+","+str(self.getHost())+":"+str(self.getPort())+")")

	def takeExposure(self):
		self.logger.info(">>>>>>>>")
		#get current exposure time
		exp = self.device.getNumber("CCD_EXPOSURE")
		# set exposure time to 5 seconds
		# etime = 1.0
		exp[0].value = self.expTime
		# send new exposure time to server/device

		# pacing goes here, wait to expose!
		if self.expConverged:
			pacetime = self.pacing - self.expTime
		else:
			self.logger.info('Rapid converging...')
			pacetime = 0.5

		self.logger.info('Pacing for {} seconds...'.format(pacetime))
		sleep(pacetime)

		self.logger.info('Exposing: {}'.format(self.expTime))
		self.sendNewNumber(exp)


	def processImage(self):

		# turn blob into an astropy.io.fits object
		fit = fits.open(self.fit)
		img = fit[0].data
		headers = fit[0].header

		# get the exposure time
		oldExpTime = headers['EXPTIME']
		# self.logger.info('Exposure time found: {}'.format(exptime))

		# get the median of the image
		imgMedian = np.median(img)
		imgMean = np.mean(img)
		# self.logger.info('Image median: {} mean: {}'.format(imgMedian, imgMean))

		# test to see if we're nearly converged
		# if so, set it as such
		if imgMedian > (2000 * self.convergeAt):
			self.expConverged = True
		else:
			self.expConverged = False

		newExptime = 4000 / (imgMedian / oldExpTime)

		if newExptime < self.minExp:
			newExptime = self.minExp

		if newExptime > self.maxExp:
			newExptime = self.maxExp
		
		self.expTime = newExptime
		# self.logger.info('New exposure time: {}'.format(newExptime))

		lastGain = self.gain

		if newExptime == self.minExp and imgMedian >= (4000*1.5):
			# set the gain to 0
			self.gain = 0
		else:
			self.gain = self.startingGain

		self.setCCDControls()


		self.logger.info('This exposure: {}@{} Next Exposure: {}@{} Median: {} Mean: {}'
						 .format(oldExpTime, lastGain, newExptime, self.gain, imgMedian, imgMean))

		f = open('/dev/shm/allsky.log', 'a+')
		log = '{},{},{}\n'.format(oldExpTime, self.expTime, imgMedian)
		f.write(log)
		f.close()

		# calbrate TODO
		img = self.calibrateImage(img)

		# convert to color
		img_color = cv2.cvtColor(img, cv2.COLOR_BAYER_GR2RGB)

		# stretch - gamma correction
		img_color = np.array(65535*(img_color / 65535) ** 0.45, dtype = 'uint16')

		# annotate
		timestamp = '12:00:00 PM'
		font = cv2.FONT_HERSHEY_SIMPLEX
		bottomRightCorner = (1115, 950)
		upperRightCorner1 = (990, 30)
		upperRightCorner2 = (1025, 60)
		fontScale = .8
		fontColor = (65535, 65535, 65535)
		lineThickness = 2

		# annotate time
		cv2.putText(
			img_color,
			datetime.datetime.now().strftime('%I:%M:%S %p'),
			bottomRightCorner,
			font,
			fontScale,
			fontColor,
			lineThickness)

		# annotate time
		cv2.putText(
			img_color,
			'Exposure: {0:.4f} sec'.format(oldExpTime),
			upperRightCorner1,
			font,
			fontScale,
			fontColor,
			lineThickness)		

		# annotate time
		cv2.putText(
			img_color,
			'Sky Median: {0:.1f}'.format(imgMedian),
			upperRightCorner2,
			font,
			fontScale,
			fontColor,
			lineThickness)

		img_color = (img_color/256).astype('uint8')
		new_width = int(img_color.shape[1] * self.resize_pct / 100)
		new_height = int(img_color.shape[0] * self.resize_pct / 100)
		img_color_resized = cv2.resize(img_color, (new_width, new_height), interpolation=cv2.INTER_AREA)

		# put the file in /dev/shm for sharing

		cv2.imwrite('/dev/shm/color.png', img_color_resized, [cv2.IMWRITE_PNG_COMPRESSION, 5]) 
		cv2.imwrite('/dev/shm/color_orig.png', img_color, [cv2.IMWRITE_PNG_COMPRESSION, 5])

	def calibrateImage(self, img):


		# medianBlur is pretty good a dealing with hot pixels.
		img = cv2.medianBlur(img, 3)

		# first determine if a master calibrator exists. If not,
		# try to make it.
		if self.masterCalibrator is None:

			# TODO - scale the master dark
			if self.masterBias is not None:
				if self.masterDark is not None:
					# create a single combined master
					self.masterCalibrator = None
				else:

					bias = fits.open(self.masterBias)
					bias = bias[0].data

					self.masterCalibrator = bias

			elif self.masterDark is not None:
				# only a master dark
				self.masterCalibrator = None

			# clear out the master bias and dark
			self.masterBias = None
			self.masterDark = None


		# now check to see if one exists. If so, use it.
		if self.masterCalibrator is not None:

			img = (img) - self.masterCalibrator
			return img

		else: # otherwise, just send the img back
			return img

	def setCCDControls(self):

		controls = self.device.getNumber('CCD_CONTROLS')
		controls[0].value = self.gain
		self.sendNewNumber(controls)


if __name__ == '__main__':

	logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
	 
	# instantiate the client
	# indiclient=IndiClient(master_bias='allsky_master_bias.fit')
	indiclient=IndiClient(resize_pct=60, gain=35)


	# set indi server localhost and port 7624
	indiclient.setServer("localhost",7624)

	# connect to indi server
	print("Connecting to indiserver")
	if (not(indiclient.connectServer())):
		 print("No indiserver running on "+indiclient.getHost()+":"+str(indiclient.getPort()))
		 sys.exit(1)

	sleep(indiclient.expTime + 3) 
	# indiclient.disconnectServer()
	# start endless loop, client works asynchron in background
	while True:
	   time.sleep(10)
	
