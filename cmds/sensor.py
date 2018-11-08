import logging
import state
import tracker
import time

logger = logging.getLogger('Sensor Update')

def update(client,args):
	room = args[0]
	newt = (float(args[1])*9.0/5.0)+32.0
	newh = float(args[2])
	
	state.rooms[room] = (newt,newh,time.time())
	tracker.trackTemp(room,newt,newh)
	logger.debug('%s %.2f°C %.2f%%' % (room,newt,newh))

handlers = {
	'sup': update
}