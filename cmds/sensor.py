import logging
import state

logger = logging.getLogger('Sensor Update')

def update(client,args):
	room = args[0]
	newt = (float(args[1])*9.0/5.0)+32.0
	newh = float(args[2])
	
	avgwo = state.avgTmp*len(state.rooms)-state.rooms[room][0] if room in state.rooms else state.avgTmp
	
	state.rooms[room] = (newt,newh)
	state.avgTmp = (avgwo+newt)/len(state.rooms)
	logger.debug('%s %.2f°C %.2f%% | avg %.2f°C' % (room,newt,newh,state.avgTmp))

handlers = {
	'sup': update
}