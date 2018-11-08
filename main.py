import logging
import sys

level = logging.DEBUG if '--debug' in sys.argv else logging.INFO
logging.basicConfig(format='[%(levelname)s] [%(name)s] %(message)s', level=level, handlers=[ logging.FileHandler("console.log"), logging.StreamHandler() ])

import state
import cmdserver
import scheduler

import signal

log = logging.getLogger('Main')

def shutdown(sig, frame):
	log.info('=======================')
	for handler in state.shutdownHandlers:
		handler()
	sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

log.info('=======================')

signal.pause()