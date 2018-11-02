import state

def fanOn(client,args):
	turnedOn = state.relays.fanOn()
	msg = b'ok' if turnedOn else b'no'
	client.send(msg)

def fanOff(client,args):
	turnedOff = state.relays.fanOff()
	msg = b'ok' if turnedOff else b'no'
	client.send(msg)

handlers = {
	'fanon': fanOn,
	'fanoff': fanOff
}