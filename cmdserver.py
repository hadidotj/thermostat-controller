import socket
import threading
import time

class CmdServer:
	
	SERVER_IP = '0.0.0.0'
	SERVER_PORT = 44147
	MAX_CLIENTS = 5
	TIMEOUT = 5
	SHUTDOWN_WAIT = 5

	def __init__(self):
		self.running = True
		self.clientList = []
		
		self.server = server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.bind((self.SERVER_IP, self.SERVER_PORT))
		server.listen(CmdServer.MAX_CLIENTS)
		
		self.serverThread = serverThread = threading.Thread(target=self.run)
		serverThread.setDaemon(True)
		serverThread.start()
		
	def run(self):
		while self.running:
			try:
				client = self.server.accept()
				self.clientList.append(client)
				threading.Thread(target=self.clientConnect, args=(client,)).start()
			except Exception as e:
				pass
				
	def clientConnect(self, client):
		client.settimeout(CmdServer.TIMEOUT)
		
		try:
			req = client.recv(1024);
			args = req.split(',')
			cmd = args.pop(0)
			
			pass
		except Exception as e:
			pass
		
		client.close()
		self.clientList.remove(client)
		
	def stop(self):
		self.running = False
		
		stopCnt = CmdServer.SHUTDOWN_WAIT
		while len(self.clientList) > 0 and stopCnt > 0:
			time.sleep(1)
			stopCnt -= 1
		
		if len(self.clientList) > 0:
			for client in self.clientList:
				client.close()
		
		self.server.close()
		self.serverThread.join(timeout=1)
