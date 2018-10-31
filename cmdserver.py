from os.path import dirname
import logging
import pkgutil
import socket
import threading
import time
import state
import sys

logger = logging.getLogger('CmdServer')

class CmdServer:
	
	SERVER_IP = ''
	SERVER_PORT = 44147
	MAX_CLIENTS = 5
	TIMEOUT = 5
	SHUTDOWN_WAIT = 5
	
	serverCreated = False
	cmdHandlers = {}

	def __init__(self):
		if(CmdServer.serverCreated):
			raise Exception('Server already started')
		CmdServer.serverCreated = True
		self.running = True
		self.clientList = []
		
		self.server = server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.bind((CmdServer.SERVER_IP, CmdServer.SERVER_PORT))
		server.listen(CmdServer.MAX_CLIENTS)
		
		self.serverThread = serverThread = threading.Thread(target=self.run)
		serverThread.start()
		
		logger.info('Started server on port %d with %d max clients' % (CmdServer.SERVER_PORT,CmdServer.MAX_CLIENTS))
		
	def run(self):
		while self.running:
			try:
				client, addr = self.server.accept()
				logger.debug('Client connected...')
				self.clientList.append(client)
				clientThread = threading.Thread(target=self.clientConnect, args=(client,))
				clientThread.start()
			except Exception as e:
				if self.running:
					logger.exception('Exception during client accept')
				
	def clientConnect(self, client):
		client.settimeout(CmdServer.TIMEOUT)
		
		try:
			req = client.recv(1024)
			logger.debug('Recevied %s' % str(req))
			args = req.decode('utf-8').split(',')
			cmd = args.pop(0)
			if(cmd in CmdServer.cmdHandlers):
				CmdServer.cmdHandlers[cmd](client, args)
			else:
				logger.warn('Received unknow command: %s %s' % (cmd, args))
		except socket.timeout as t:
			logger.warn('Client took too long to send a command')
		except Exception as e:
			logger.exception('Exception during client processing')
		
		client.close()
		self.clientList.remove(client)
		
	def stop(self):
		logger.info('Server shutdown inititated')
		self.running = False
		
		stopCnt = CmdServer.SHUTDOWN_WAIT
		while len(self.clientList) > 0 and stopCnt > 0:
			logger.warn('Waiting %d seconds for %d active connections' % (stopCnt,len(self.clientList)))
			time.sleep(1)
			stopCnt -= 1
		
		if len(self.clientList) > 0:
			logger.warn('%d clients being disconnected' % len(self.clientList))
			for client in self.clientList:
				client.close()
		
		self.server.close()
		self.serverThread.join(timeout=1)
		logger.info('Server shutdown successfully')

mainServer = CmdServer()
state.shutdownHandlers.append(mainServer.stop)

dir = dirname(__file__) + '/cmds'
for importer, package_name, _ in pkgutil.iter_modules([dir]):
	full_package_name = 'cmds.' + package_name
	if full_package_name not in sys.modules:
		module = importer.find_module(package_name).load_module(package_name)
		CmdServer.cmdHandlers[module.cmd] = module.handler
		logger.info('Loaded command [%s]' % module.cmd)