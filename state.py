from relays import Relays
import tracker
import os
import json
import logging

logger = logging.getLogger('State')

relays = Relays()
rooms = {}
tmpHold = False
settings = {}
weather = {}

# First, load defaults (or newly added settings
try:
    with open('settings.default.json') as df:
        settings = json.load(df)
except:
    logger.error('Could not load default settings file!')

# Now try and load settings from a saved settings file
try:
    with open('settings.json') as f:
        settings = {**settings, **json.load(f)}
        logger.info('Loaded settings from file:')
        logger.info(settings)
except:
    logger.warning('Settings file not found. Using default file!')

# Set the current avgTmp to the current setTmp
avgTmp = settings['setTmp']


# Save settings during shutdown!
def saveSettings():
    logger.info('Saving settings to file.')
    try:
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
    except:
        logger.error('Could not save settings to file!')


# Insure all relays are turned off if shutting down!
def relaysOff():
    logger.info('Turning off all relays!')
    relays.fanOff()
    relays.heatOff()
    relays.coolOff()


shutdownHandlers = [saveSettings, relaysOff, tracker.shutdown]
