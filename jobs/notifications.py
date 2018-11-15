from scheduler import Job
import logging
import smtplib
import state
import time

log = logging.getLogger('Notifications')

class Notifications(Job):

	def __init__(self):
		super(Notifications, self).__init__()
		self.last_nosense_time = None
		self.last_sensor_time = None
		self.last_sensor_count = 0
		self.last_temp_time = None
		self.last_temp_count = 0
		self.last_warn_time = None
		self.skip_count = 12

	def process(self):
		self.skip_count-=1
		if self.skip_count>0:
			return
		
		currentTime = time.time()
		hour = 3600
		
		# Check if there are any sensors in the first place...
		if len(state.rooms) == 0:
			if self.last_nosense_time is None or self.last_nosense_time+hour <= currentTime:
				self.last_nosense_time = time.time()
				self.notifyNoSensors()
		
		inactiveRooms = []
		tempWarnings = []
		minAgo = time.time()-60
		roomnames = state.settings['roomnames']
		for name in state.rooms:
			room = state.rooms[name]
			dispName = roomnames[name] if name in roomnames else name
			if room[2] <= minAgo:
				inactiveRooms.append(dispName)
			elif room[0] >= state.settings['toHot'] or room[0] <= state.settings['toCold']:
				tempWarnings.append('%s is %.2fF' % (dispName,room[0]))
		
		# First, notify if there are any room sensors that are no longer active
		inactiveCount = len(inactiveRooms)
		if inactiveCount > 0:
			if inactiveCount!=self.last_sensor_count or self.last_sensor_time is None or self.last_sensor_time+hour <= currentTime:
				self.last_sensor_time = time.time()
				self.notifySensorInactive(inactiveRooms)
		self.last_sensor_count = inactiveCount
		
		# check for temperature warnings
		tempCount = len(tempWarnings)
		if tempCount > 0:
			if tempCount!=self.last_temp_count or self.last_temp_time is None or self.last_temp_time+hour <= currentTime:
				self.last_temp_time = time.time()
				self.notifyTempWarning(tempWarnings)
		self.last_temp_count = tempCount
		
		# check for long run times
		relays = state.relays
		fanTime = (relays.fan_time is not None and relays.fan_time+hour <= currentTime)
		heatTime = (relays.heat_time is not None and relays.heat_time+hour <= currentTime)
		coolTime = (relays.cool_time is not None and relays.cool_time+hour <= currentTime)
		if fanTime or heatTime or coolTime:
			if self.last_warn_time is None or self.last_warn_time+hour <= currentTime:
				self.last_warn_time = time.time()
				self.notifyLongTime(fanTime, heatTime, coolTime)
	
	def notifyNoSensors(self):
		log.info('Sending No Sensors Notification')
		self.sendNotification('NO SENSORS')
		
	def notifySensorInactive(self, inactiveRooms):
		log.info('Sending Sensor Fail Notification')
		msg = 'SENSOR FAIL\n'
		for room in inactiveRooms:
			msg += room + '\n'
		self.sendNotification(msg)
		
	def notifyTempWarning(self, tempWarnings):
		log.info('Sending Temp Warning Notification')
		msg = 'TEMP WARNING\n'
		for warn in tempWarnings:
			msg += warn + '\n'
		self.sendNotification(msg)
		
	def notifyLongTime(self, fanTime, heatTime, coolTime):
		log.info('Sending Long Run Notification')
		relays = state.relays
		currentTime = time.time()
		msg = 'LONG RUNTIME\n'
		if fanTime:
			msg += 'Fan %.2fmin\n' % ((currentTime-relays.fan_time)/60)
		if heatTime:
			msg += 'Heat %.2fmin\n' % ((currentTime-relays.heat_time)/60)
		if coolTime:
			msg += 'Cool %.2fmin\n' % ((currentTime-relays.cool_time)/60)
		self.sendNotification(msg)
		
	def sendNotification(self, msg):
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login('hadidotj@gmail.com', 'mqncohgvigppqaqo')
		 
		server.sendmail('hadidotj@gmail.com', ['6145812604@vtext.com'], msg)
		server.quit()

Notifications()