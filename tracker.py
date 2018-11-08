import logging
import os.path
import state
import sqlite3
import threading
import time

log = logging.getLogger('Tracker')

DATABASE_FILE = 'thermostat.db'

# First, determine if we need to create the DataBase
isNew = not os.path.isfile(DATABASE_FILE)

# Open the DataBase file
db = None
dbLock = threading.Lock()
log.info('Tracker started up as %s instance' % ('a new' if isNew else 'an existing'))

relays = {}
sensors = {}

def connect():
	global db
	db = sqlite3.connect(DATABASE_FILE)
	return db.cursor()
	
def disconnect(cursor):
	global db
	cursor.close()
	db.close()
	db = None

def init():
	with dbLock:
		cursor = connect()
		try:
			if isNew:
				SENSOR_TABLE = 'CREATE TABLE IF NOT EXISTS sensors (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)'
				TEMPHIST_TABLE = 'CREATE TABLE IF NOT EXISTS temphistory (id INTEGER PRIMARY KEY, sensor INTEGER NOT NULL REFERENCES sensors(id), time REAL NOT NULL, temp REAL NOT NULL, humid REAL NOT NULL)'
				RELAY_TABLE = 'CREATE TABLE IF NOT EXISTS relays (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)'
				RELAY_INSERT = 'INSERT INTO relays (name) VALUES(?)'
				RELAYHIST_TABLE = 'CREATE TABLE IF NOT EXISTS relayhistory (id INTEGER PRIMARY KEY, relay INTEGER NOT NULL REFERENCES relays(id), time REAL NOT NULL, state INTEGER NOT NULL)'
				
				cursor.execute(SENSOR_TABLE)
				cursor.execute(TEMPHIST_TABLE)
				cursor.execute(RELAY_TABLE)
				cursor.execute(RELAYHIST_TABLE)
				
				cursor.executemany(RELAY_INSERT, [('FAN',),('HEAT',),('COOL',)])
				
				db.commit()
			
			cursor.execute('SELECT id,name FROM relays')
			for relay in cursor:
				relays[relay[1]] = relay[0]
				
			log.info('Loaded %d relay IDs from DataBase' % len(relays))

			cursor.execute('SELECT id,name FROM sensors')
			for sensor in cursor:
				sensors[sensor[1]] = sensor[0]
				
			log.info('Loaded %d sensor IDs from DataBase' % len(sensors))
		finally:
			disconnect(cursor)
	
def trackRelay(name, value):
	with dbLock:
		cursor = connect()
		try:
			id = relays[name] if name in relays else None
			if id is None:
				cursor.execute('INSERT INTO relays (name) VALUES (?)', (name,))
				id = cursor.lastrowid
				relays[name] = id
				db.commit()
				
			query = 'INSERT INTO relayhistory (relay, time, state) VALUES (?,?,?)'
			data = (id, time.time(), value)
			cursor.execute(query, data)
			db.commit()
		finally:
			disconnect(cursor)
		
def trackTemp(sensor, temp, humid):
	with dbLock:
		cursor = connect()
		try:
			id = sensors[sensor] if sensor in sensors else None
			if id is None:
				cursor.execute('INSERT INTO sensors (name) VALUES (?)', (sensor,))
				id = cursor.lastrowid
				sensors[sensor] = id
				db.commit()
			
			query = 'INSERT INTO temphistory (sensor, time, temp, humid) VALUES (?,?,?,?)'
			data = (id, time.time(), temp, humid)
			cursor.execute(query, data)
			db.commit()
		finally:
			disconnect(cursor)

def shutdown():
	log.info('Shutting down')
	try:
		db.interrupt()
	except:
		pass
		
	locked = dbLock.acquire(False)
	if not locked:
		log.info('Waiting for Database Lock')
		if not dbLock.acquire(timeout=5):
			log.warn('Database Lock NOT acquired! May corrupt the database...')

	log.info('Database Closed')

init()