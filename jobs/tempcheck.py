from scheduler import Job
import logging
import state

log = logging.getLogger('TempCheck')

class TempCheck(Job):
	def process(self):

		avgTmp = state.avgTmp
		relays = state.relays
		settings = state.settings
		
		setTmp = settings['setTmp']
		offset = settings['offset']
		mode = settings['mode']
		
		# If the mode is OFF, make sure everything is off
		if mode == 'OFF':
			if relays.isHeatOn():
				relays.heatOff()
				
			if relays.isCoolOn():
				relays.coolOff()
		
		# Is current temp below set temp?
		elif avgTmp < setTmp-offset:
			log.debug('Burrr... It\'s two cold now!')

			# Turn off cool
			if relays.isCoolOn():
				relays.coolOff()
			
			# Or turn heat on
			elif mode == 'HEAT' and not relays.isHeatOn():
				relays.heatOn()
			
			# Or maybe we switched modes?
			elif mode == 'COOL' and relays.isHeatOn():
				relays.heatOff()
		
		# Is the current temp above set temp?
		elif avgTmp > setTmp+offset:
			log.debug('Ahhh! It\'s too hot now!')
			
			# Turn off heat
			if relays.isHeatOn():
				relays.heatOff()
				
			# Or turn cool on
			elif mode == 'COOL' and not relays.isCoolOn():
				relays.coolOn()
				
			# Or maybe we switched modes
			elif mode == 'HEAT' and relays.isCoolOn():
				relays.coolOff()

TempCheck()