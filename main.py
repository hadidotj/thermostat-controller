import logging
logging.basicConfig(format='[%(levelname)s] [%(name)s] %(message)s', level=logging.DEBUG, handlers=[ logging.FileHandler("console.log"), logging.StreamHandler() ])

import cmdserver
import signal
import state
import sys

def shutdown(sig, frame):
	for handler in state.shutdownHandlers:
		handler()
	sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

signal.pause()