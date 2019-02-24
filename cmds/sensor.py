import logging
import state
import tracker
import time
import room

logger = logging.getLogger('Sensor Update')


def update(client, args):
    id = args[0]
    newt = (float(args[1]) * 9.0 / 5.0) + 32.0
    newh = float(args[2])

    if id not in state.rooms:
        state.rooms[id] = room.Room()
    sensor = state.rooms[id]

    sensor.record(newt, newh)
    tracker.trackTemp(id, newt, newh)
    logger.debug('%s %.2f°F %.2f%%' % (id, newt, newh))
    time.sleep(1)


handlers = {
    'sup': update
}
