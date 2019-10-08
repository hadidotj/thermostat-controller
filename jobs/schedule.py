from scheduler import Job
import logging
import state
import datetime

log = logging.getLogger('AutoSchedule')

currentSchedule = None

class AutoSchedule(Job):

	def process(self):
		global currentSchedule
	
		# If the temp is held, don't let the schedule change it!
		if state.tmpHold:
			log.debug('Temp held. Not checking schedule.')
			return
			
		# Reset the schedule if set to OFF and return
		mode = state.settings['mode']
		if mode == 'OFF':
			currentSchedule = None
			log.debug('Current mode is OFF. No schedule change necessary.')
			return
		
		# Skip out if there is no schedule for this mode
		schedules = state.settings['schedule']
		if mode not in schedules:
			log.warn('No schedule created for %s mode.' % mode)
			return
		
		# Get what scheduled time we should be in now
		schedule = schedules[mode]
		now = datetime.datetime.today()
		dayOfWork = now.weekday()
		name = 'weekday' if dayOfWork<5 else 'weekend'
		log.debug('Day Of week is %d which is a %s' % (dayOfWork,name))
		
		# Look for the current schedule, based on time
		use = schedule[name]
		hour = now.hour
		min = now.minute
		currentTemp = state.settings['setTmp']
		changeSchedule = None
		changeTime = None
		changeTo = currentTemp
		
		# For each scheduled time...
		for d in use:
			s = next(iter(d))
			inx = s.index(':')
			shr = int(s[:inx])
			smin = int(s[inx+1:])
			
			# Check if it has passed
			if shr<hour or (shr==hour and smin<=min):
				changeSchedule = d
				changeTime = s
				changeTo = d[s]
				
		# Skip if the current schedule is still running. This allows overrides to the current schedule
		if changeSchedule is currentSchedule:
			log.debug('No schedule change.')
			return
		
		# otherwise, we changed schedules!
		currentSchedule = changeSchedule
		if currentTemp != changeTo:
			log.info('Scheduled setTmp change: %.2f to %.2f at %s' % (currentTemp,changeTo,changeTime))
			state.settings['setTmp'] = changeTo
		else:
			log.debug('No change at this time')


AutoSchedule()