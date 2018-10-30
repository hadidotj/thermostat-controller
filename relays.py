from gpiozero import OutputDevice

class Relays:

    FAN_PIN = 14
    HEAT_PIN = 15
    COOL_PIN = 18

    def __init__(self):
        self.fan = OutputDevice(Relays.FAN_PIN)
        self.heat = OutputDevice(Relays.HEAT_PIN)
        self.cool = OutputDevice(Relays.COOL_PIN)

    def isFanOn(self):
        return self.fan.value;

    def fanOn(self):
        if(not self.fan.value):
            self.fan.on()
            return True
        return False

    def fanOff(self):
        if(self.fan.value):
            self.fan.off()
            return True
        return False

    def isHeatOn(self):
        return self.heat.value;

    def heatOn(self):
        if(not self.heat.value and not self.cool.value):
            self.heat.on()
            return True
        return False

    def heatOff(self):
        if(self.heat.value):
            self.heat.off()
            return True
        return False

    def isCoolOn(self):
        return self.cool.value;

    def coolOn(self):
        if(not self.cool.value and not self.heat.value):
            self.cool.on()
            return True
        return False

    def coolOff(self):
        if(self.cool.value):
            self.cool.off()
            return True
        return False

    def status(self):
        if(self.heat.value):
            return "HEAT"
        elif(self.cool.value):
            return "COOL"
        elif(self.fan.value):
            return "FAN"
        return "OFF"
