import json
import state

def fanOn(client,args):
	turnedOn = state.relays.fanOn()
	msg = b'ok' if turnedOn else b'no'
	client.send(msg)

def fanOff(client,args):
	turnedOff = state.relays.fanOff()
	msg = b'ok' if turnedOff else b'no'
	client.send(msg)
	
def setMode(client,args):
	state.settings['mode'] = args[0]
	client.send(('Mode changed to %s' % args[0]).encode())

def setTmp(client,args):
	state.settings['setTmp'] = float(args[0])
	client.send(b'ok')

def setOffset(client,args):
	state.settings['offset'] = float(args[0])
	client.send(b'ok')
	
def status(client,args):
	relays = state.relays
	dict = {
		'avgTmp':state.avgTmp,
		'rooms':state.rooms,
		'settings':state.settings,
		'heat':{'running': relays.isHeatOn(), 'time': relays.heat_time},
		'cool':{'running': relays.isCoolOn(), 'time': relays.cool_time},
		'fan':{'running': relays.isFanOn(), 'time': relays.fan_time}
	}
	client.send(json.dumps(dict).encode())

handlers = {
	'fanon': fanOn,
	'fanoff': fanOff,
	'mode': setMode,
	'setTmp': setTmp,
	'offset': setOffset,
	'status': status
}
