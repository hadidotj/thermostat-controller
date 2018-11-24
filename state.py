from relays import Relays
import tracker
import os
import json
import logging

logger = logging.getLogger('State');

relays = Relays()
rooms = {}
tmpHold = False
settings = {
	'setTmp': 70,
	'offset':1.0,
	'mode': 'OFF',
	'toHot': 80,
	'toCold': 60,
	'roomnames': {
		'bf88cfe0': 'Living',
		'bf83c180': 'Bed'
	},
	'schedule': {
		'weekday': [{'5:30':69.0},{'8:00':65.0},{'16:30':70.0},{'23:00':65.0}],
		'weekend': [{'6:00':70.00},{'23:00':65.0}]
	}
}

# Load the settings from the settings file!
try:
	with open('settings.json') as f:
		settings = {**settings, **json.load(f)}
		logger.info('Loaded settings from file')
		logger.info(settings)
except:
	logger.warn('Settings file not found... Using defaults!')
	
avgTmp = settings['setTmp']

# Save settings durning shutdown!
def saveSettings():
	logger.info('Saving settings to file.')
	try:
		with open('settings.json', 'w') as f:
			json.dump(settings, f)
	except:
		logger.error('Could not save settings to file!')

# Insure all relays are turned off if shutting down!
def relaysOff():
	logger.info('Turning off all relays!')
	relays.fanOff()
	relays.heatOff()
	relays.coolOff()

shutdownHandlers = [saveSettings,relaysOff,tracker.shutdown]