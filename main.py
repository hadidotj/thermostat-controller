from cmdserver import CmdServer
import logging
import signal
import sys

logging.basicConfig(format='[%(levelname)s] [%(name)s] %(message)s', level=logging.DEBUG)

server = None

def shutdown(sig, frame):
	if(server is not None):
		server.stop()
	sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

server = CmdServer()

signal.pause()