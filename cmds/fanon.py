import state

def fanOn(client,args):
	turnedOn = state.relays.fanOn()
	msg = 'ok' if turnedOn else 'no'
	client.send(msg.encode('utf-8'))

def fanOff(client,args):
	turnedOff = state.relays.fanOff()
	msg = 'ok' if turnedOff else 'no'
	client.send(msg.encode('utf-8'))

handlers = {
	'fanon': fanOn,
	'fanoff': fanOff
}