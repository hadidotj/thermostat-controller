from os.path import dirname
import logging
import pkgutil
import state
import sys
import threading
import time

logger = logging.getLogger('Scheduler')

class Scheduler:

	DEFAULT_TICK = 5
	DEFAULT_DELAY = DEFAULT_TICK
	
	jobs = []
	tick = DEFAULT_TICK

	def __init__(self):
		self.running = True
		self.jobThread = threading.Thread(target=self.run)
		self.jobThread.start()
		
	def run(self):
		while self.running:
			try:
				time.sleep(Scheduler.tick)
				# Gah! Conccurent modification to Scheduler.jobs for one time jobs!
				jobList = Scheduler.jobs.copy()
				for job in jobList:
					if self.running and job.shouldRun():
						job.start()
			except:
				logger.exception('Main scheduler thread encountered error during job processing')

	def stop(self):
		logger.info('Scheduler shutdown inititated. %d current scheduled jobs' % len(Scheduler.jobs))
		
		self.running = False
		
		# Gah! We need to copy the list because Job.stop removes from Scheduler.jobs,
		# and some jobs don’t get Job.stop called because the original list changed!
		# No conccurrent modification exception...
		stopList = Scheduler.jobs.copy()
		for job in stopList:
			job.stop()
		
		stopCnt = int(Scheduler.tick*1.5)
		while len(Scheduler.jobs) > 0 and stopCnt > 0:
			logger.warn('Waiting %d seconds for %d active jobs to stop' % (stopCnt,len(Scheduler.jobs)))
			time.sleep(1)
			stopCnt -= 1
			
		if len(Scheduler.jobs) > 0:
			logger.warn('%d active jobs have not been shutdown! This may lead to a corrupt state.' % len(Scheduler.jobs))
			for job in Scheduler.jobs:
				logger.warn('> %s [%s][%s]' % (job.__class__.__name__, 'STOP' if job.stopflag else 'ACTIVE', 'WAITING' if job.processThread is None else 'RUNNING'))
				if job.processThread is not None:
					job.processThread.join(timeout=1)
		
		self.jobThread.join(timeout=1)
		logger.info('Scheduler shutdown successfully')

class Job:

	def __init__(self, delay=Scheduler.DEFAULT_DELAY):
		self.stopflag = False
		self.delay = self.tick = delay
		self.processThread = None
		Scheduler.jobs.append(self)
		
	def shouldRun(self):
		self.tick -= Scheduler.tick
		return self.tick <= 0 and not self.stopflag
	
	def start(self):
		if self.processThread is None and not self.stopflag:
			self.processThread = threading.Thread(target=self.run)
			self.processThread.setDaemon(True)
			self.processThread.start()
	
	def run(self):
		try:
			self.process()
		except:
			logger.exception('%s threw error during processing' % __class__)
		finally:
			self.tick = self.delay
			self.processThread = None
			
			if self.stopflag:
				self.stopinternal()
				
	def process(self):
		logger.error('%s does not override the Job.process method. Stopping this job.' % self.__class__.__name__)
		self.stop()
			
	def stop(self):
		logger.debug('Stopping job %s' % self.__class__.__name__)
		self.stopflag = True
		if self.processThread is None:
			self.stopinternal()
			
	def stopinternal(self):
		Scheduler.jobs.remove(self)
		
class OneTimeJob(Job):
	def run(self):
		super().run()
		
		if not self.stopflag:
			self.stop()

mainScheduler = Scheduler()
state.shutdownHandlers.insert(1, mainScheduler.stop)

dir = dirname(__file__) + '/jobs'
for importer, package_name, _ in pkgutil.iter_modules([dir]):
	full_package_name = 'jobs.' + package_name
	if full_package_name not in sys.modules:
		module = importer.find_module(package_name).load_module(package_name)
		logger.info('Loaded job [%s]' % package_name)