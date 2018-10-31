import state

cmd='fanon'

def fanOn(client,args):
	turnedOn = state.relays.fanOn()
	msg = 'ok' if turnedOn else 'no'
	client.send(msg.encode('utf-8'))

handler = fanOn