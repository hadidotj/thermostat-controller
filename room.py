import logging
import time

logger = logging.getLogger('Room')


class Room:

    temps = []
    humids = []

    curTemp = 0.0
    curHumid = 0.0

    offline = False
    lastUpdate = None

    def record(self, temp, humid):
        self.curTemp = self.calc(self.temps, self.curTemp, temp)
        self.curHumid = self.calc(self.humids, self.curHumid, humid)
        self.offline = False
        self.lastUpdate = time.time()

    def calc(self, arr, oldVal, newVal):
        arrlen = len(arr)

        if arrlen >= 12:
            arr.pop(0)
        arr.append(newVal)

        # Copy the array before sorting... we don't want to remove the smallest reading
        # during the next update we want to remove the oldest!
        c = arr.copy()
        c.sort()
        qi = int(arrlen/4)
        q1 = c[qi]
        q3 = c[arrlen-qi]
        qr = (q3-q1)*1.5
        tmin = q1-qr
        tmax = q3+qr

        logger.debug('%.2f <= %.2f <= %.2f ==> %.2f' % (tmin, newVal, tmax, newVal if tmin <= newVal <= tmax else oldVal))

        return newVal if tmin <= newVal <= tmax else oldVal

    def read(self):
        return self.curTemp, self.curHumid, self.lastUpdate
