from cmdserver import CmdServer
import signal
import sys

server = None

def shutdown(sig, frame):
	if(server is not None):
		server.stop()
	sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

server = CmdServer()

signal.pause()