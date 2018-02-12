from gpio.emulateddevice import EmulatedDevice
from gpio.raspberrypi3 import RaspberryPi3GPIO

DEVICE_TYPE = {"RaspberryPi3": RaspberryPi3GPIO,
               "Emulator": EmulatedDevice}

class IoTDevice():
    @classmethod
    def create(cls, device_type, protocol, address, port, username, password):
        return DEVICE_TYPE[device_type](protocol, address, port, username, password)
