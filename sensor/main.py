from dht import DHT22
from machine import Pin, unique_id
import network
import socket
import time

print('Starting up')

LED = Pin(2, Pin.OUT)
LED.value(1)
time.sleep(1)
LED.value(0)
time.sleep(1)
LED.value(1)
time.sleep(1)
LED.value(0)
time.sleep(1)

sensor = DHT22(Pin(14, Pin.IN, Pin.PULL_UP))

wlan = None
name = str(unique_id())[4:-1].replace('\\x','')

def blink(cnt,wait=0.2):
	for i in range(0, cnt):
		LED.value(1)
		time.sleep(wait)
		LED.value(0)
		time.sleep(wait)
		
def connectWifi():
	global wlan
	if wlan is None:
		LED.value(1)
		print('Creating new network WLAN')
		wlan = network.WLAN(network.STA_IF)
		LED.value(0)
		
	if not wlan.active() or not wlan.isconnected():
		LED.value(1)
		print('Connecting to network')
		wlan.active(True)
		wlan.connect('ParrotHeadsOnly', '6145812604')
		
		cntCnt = 0
		while not wlan.isconnected() and cntCnt <= 5:
			print('...')
			cntCnt += 1
			time.sleep(1)
			LED.value(0)
			blink(cntCnt)
			LED.value(1)
			
		time.sleep(1)
		LED.value(0)
		
		if not wlan.isconnected():
			print('Still not connected')
			blink(6, 0.5)
			time.sleep(2)
			blink(6, 0.5)
			return False
			
		print('Connected! ' + str(wlan.ifconfig()))
		blink(1)
			
	return True

def readSensor():
	try:
		sensor.measure()
		t = sensor.temperature()
		h = sensor.humidity()
		
		if isinstance(t, float) and isinstance(h, float):
			c = socket.socket()
			c.settimeout(5)
			try:
				c.connect(('192.168.1.3', 44147))
				c.send(('sup,%s,%.2f,%.2f' % (name, t, h)).encode())
				print(('sup,%s,%.2f,%.2f' % (name, (t*9.0/5.0)+32, h)).encode())
				blink(1,0.1)
			except Exception as e:
				print('Connection error')
				blink(2)
			c.close()
		else:
			print('Read error')
			blink(3)
	except Exception as e:
		print('Exception: ' + str(e))
		blink(4)
		
while True:
	if connectWifi():
		readSensor()
	time.sleep(5)