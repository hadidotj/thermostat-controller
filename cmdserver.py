import logging
import socket
import threading
import time

logger = logging.getLogger('CmdServer')

class CmdServer:
	
	SERVER_IP = ''
	SERVER_PORT = 44147
	MAX_CLIENTS = 5
	TIMEOUT = 5
	SHUTDOWN_WAIT = 5

	def __init__(self):
		self.running = True
		self.clientList = []
		
		self.server = server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.bind((CmdServer.SERVER_IP, CmdServer.SERVER_PORT))
		server.listen(CmdServer.MAX_CLIENTS)
		
		self.serverThread = serverThread = threading.Thread(target=self.run)
		serverThread.setDaemon(True)
		serverThread.start()
		
		logger.info('Started server on port %d with %d max clients' % (CmdServer.SERVER_PORT,CmdServer.MAX_CLIENTS))
		
	def run(self):
		while self.running:
			try:
				client = self.server.accept()
				logger.debug('Client connected...')
				self.clientList.append(client)
				threading.Thread(target=self.clientConnect, args=(client,)).start()
			except Exception as e:
				logger.error('Exception during client accept: %s' % str(e))
				
	def clientConnect(self, client):
		client.settimeout(CmdServer.TIMEOUT)
		
		try:
			req = client.recv(1024);
			args = req.split(',')
			cmd = args.pop(0)
			logger.debug('CMD received: %s [%s]' % (cmd, args))
		except Exception as e:
			logger.error('Exception during client processing: %s' % str(e))
		
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
