from relays import Relays
import os
import json
import logging

logger = logging.getLogger('State');

relays = Relays()
settings = {'setTmp': 70, 'offset':1.5, 'mode': 'OFF'}
rooms = {}

# Load the settings from the settings file!
try:
	with open('settings.json') as f:
		settings = json.load(f)
except:
	logger.warn('Settings file not found... Using defaults!')
	
avgTmp = settings['setTmp']

# Save settings durning shutdown!
def saveSettings():
	try:
		with open('settings.json', 'w') as f:
			json.dump(settings, f)
	except:
		logger.error('Could not save settings to file!')

# Insure all relays are turned off if shutting down!
def relaysOff():
	relays.fanOff()
	relays.heatOff()
	relays.coolOff()

shutdownHandlers = [saveSettings,relaysOff]