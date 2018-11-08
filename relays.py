from gpiozero import OutputDevice
import logging
import tracker

logger = logging.getLogger('Relays')

class Relays:

	FAN_PIN = 14
	HEAT_PIN = 15
	COOL_PIN = 18

	def __init__(self):
		self.fan = OutputDevice(Relays.FAN_PIN)
		self.heat = OutputDevice(Relays.HEAT_PIN)
		self.cool = OutputDevice(Relays.COOL_PIN)

	def isFanOn(self):
		return self.fan.value;

	def fanOn(self):
		if(not self.fan.value):
			self.fan.on()
			tracker.trackRelay('FAN', 1)
			logger.info('Fan ON')
			return True
		return False

	def fanOff(self):
		if(self.fan.value):
			self.fan.off()
			tracker.trackRelay('FAN', 0)
			logger.info('Fan OFF')
			return True
		return False

	def isHeatOn(self):
		return self.heat.value;

	def heatOn(self):
		if(not self.heat.value and not self.cool.value):
			self.heat.on()
			tracker.trackRelay('HEAT', 1)
			logger.info('Heat ON')
			return True
		return False

	def heatOff(self):
		if(self.heat.value):
			self.heat.off()
			tracker.trackRelay('HEAT', 0)
			logger.info('Heat OFF')
			return True
		return False

	def isCoolOn(self):
		return self.cool.value;

	def coolOn(self):
		if(not self.cool.value and not self.heat.value):
			self.cool.on()
			tracker.trackRelay('COOL', 1)
			logger.info('Cool ON')
			return True
		return False

	def coolOff(self):
		if(self.cool.value):
			self.cool.off()
			tracker.trackRelay('COOL', 0)
			logger.info('Cool OFF')
			return True
		return False

	def status(self):
		if(self.heat.value):
			return "HEAT"
		elif(self.cool.value):
			return "COOL"
		elif(self.fan.value):
			return "FAN"
		return "OFF"
