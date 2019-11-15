from scheduler import Job
import logging
import smtplib
import state
import time
import util

log = logging.getLogger('Notifications')


class Notifications(Job):
    def __init__(self):
        super(Notifications, self).__init__()
        self.last_nosense_time = None
        self.last_sensor_time = None
        self.last_sensor_count = 0
        self.last_temp_time = None
        self.last_temp_count = 0
        self.last_warn_time = None
        self.relay_time = [None, None, None]
        self.skip_count = 12

    def process(self):
        self.skip_count -= 1
        if self.skip_count > 0 or 'email' not in state.settings:
            return

        currentTime = time.time()
        hour = 3600
        halfHour = hour / 2

        # Check if there are any sensors in the first place...
        if len(state.rooms) == 0:
            if self.last_nosense_time is None or self.last_nosense_time + hour <= currentTime:
                self.last_nosense_time = time.time()
                self.notifyNoSensors()
        elif self.last_nosense_time is not None:
            self.notifyNoSensors(False)
            self.last_nosense_time = None

        inactiveRooms = []
        tempWarnings = []
        minAgo = time.time() - 60
        roomnames = state.settings['roomnames']
        for name in state.rooms:
            room = state.rooms[name]
            temp = room.read()[0]
            dispName = roomnames[name] if name in roomnames else name
            if room.offline:
                inactiveRooms.append(dispName)
            elif temp >= state.settings['toHot'] or temp <= state.settings['toCold']:
                tempWarnings.append('%s is %.2fF' % (dispName, temp))

        # First, notify if there are any room sensors that are no longer active
        inactiveCount = len(inactiveRooms)
        if inactiveCount > 0:
            if inactiveCount != self.last_sensor_count or self.last_sensor_time is None or self.last_sensor_time + hour <= currentTime:
                self.last_sensor_time = time.time()
                self.notifySensorInactive(inactiveRooms)
        elif self.last_sensor_time is not None:
            self.notifySensorInactive(inactiveRooms)
            self.last_sensor_time = None
        self.last_sensor_count = inactiveCount

        # check for temperature warnings
        tempCount = len(tempWarnings)
        if tempCount > 0:
            if tempCount != self.last_temp_count or self.last_temp_time is None or self.last_temp_time + 300 <= currentTime:
                self.last_temp_time = time.time()
                self.notifyTempWarning(tempWarnings)
        elif self.last_temp_time is not None:
            self.notifyTempWarning(tempWarnings)
            self.last_temp_time = None
        self.last_temp_count = tempCount

        # check for long run times
        relays = state.relays
        fanTime = (relays.fan_time is not None and relays.fan_time + halfHour <= currentTime)
        heatTime = (relays.heat_time is not None and relays.heat_time + halfHour <= currentTime)
        coolTime = (relays.cool_time is not None and relays.cool_time + halfHour <= currentTime)
        if fanTime or heatTime or coolTime:
            if self.last_warn_time is None or self.last_warn_time + halfHour <= currentTime:
                self.last_warn_time = time.time()
                self.notifyLongTime(fanTime, heatTime, coolTime)
        elif self.last_warn_time is not None:
            self.notifyLongTime(False, False, False)
            self.last_warn_time = None

    def notifyNoSensors(self, nosense=True):
        log.info('Sending No Sensors Notification')
        self.sendNotification('NO SENSORS' if nosense else ('%d Sensors Connected' % len(state.rooms)))

    def notifySensorInactive(self, inactiveRooms):
        log.info('Sending Sensor Fail Notification')
        if len(inactiveRooms) > 0:
            msg = 'SENSOR FAIL\n'
            for room in inactiveRooms:
                msg += room + '\n'
            self.sendNotification(msg)
        else:
            self.sendNotification('SENSORS RESTORED')

    def notifyTempWarning(self, tempWarnings):
        log.info('Sending Temp Warning Notification')
        if len(tempWarnings) > 0:
            msg = 'TEMP WARNING\n'
            for warn in tempWarnings:
                msg += warn + '\n'
        else:
            msg = 'TEMP RESTORED'
        self.sendNotification(msg)

    def notifyLongTime(self, fanTime, heatTime, coolTime):
        log.info('Sending Long Run Notification')
        relays = state.relays
        currentTime = time.time()
        msg = 'LONG RUNTIME\n'
        if not fanTime and not heatTime and not coolTime:
            msg = 'RUN END\n'
            if self.relay_time[0] is not None:
                msg += 'Fan Ran %.2fmin\n' % util.fmtTime((currentTime - self.relay_time[0]) / 60)
            if self.relay_time[1] is not None:
                msg += 'Heat Ran %.2fmin\n' % util.fmtTime((currentTime - self.relay_time[1]) / 60)
            if self.relay_time[2] is not None:
                msg += 'Cool Ran %.2fmin\n' % util.fmtTime((currentTime - self.relay_time[2]) / 60)
            self.relay_time = [None, None, None]
        if fanTime:
            msg += 'Fan %.2fmin\n' % util.fmtTime((currentTime - relays.fan_time) / 60)
            self.relay_time[0] = util.relays.fan_time
        if heatTime:
            msg += 'Heat %.2fmin\n' % fmtTime((currentTime - relays.heat_time) / 60)
            self.relay_time[1] = util.relays.heat_time
        if coolTime:
            msg += 'Cool %.2fmin\n' % fmtTime((currentTime - relays.cool_time) / 60)
            self.relay_time[2] = util.relays.cool_time
        self.sendNotification(msg)

    def sendNotification(self, msg):
        eset = state.settings['email']
        server = smtplib.SMTP(eset['server'], eset['port'])
        server.starttls()
        server.login(eset['user'], eset['password'])

        server.sendmail(eset['from'], eset['to'], msg)
        server.quit()


Notifications()
