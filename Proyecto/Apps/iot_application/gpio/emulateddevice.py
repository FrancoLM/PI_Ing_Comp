import random

from gpio.basegpio import BaseGPIO


class EmulatedDevice(BaseGPIO):

    def __init__(self, protocol, address, port, username, password):
        super().__init__(protocol, address, port, username, password)

    def setup_input_gpio(self, pin_number):
        # GPIO.setup(pin_number, pin_config[gpio_direction])
        self.input_gpio[pin_number] = None

    def setup_output_gpio(self, pin_number):
        # GPIO.setup(pin_number, pin_config[gpio_direction])
        self.output_gpio[pin_number] = None

    def get_input_value(self, pin_index):
        telemetry_value = random.randint(0, 100)
        print("Value to send by Emulated device: '{telemetry}'".format(telemetry=telemetry_value))
        self.input_gpio[pin_index] = telemetry_value
        return telemetry_value

    def set_output_value(self, pin_index, value):
        self.output_gpio[pin_index] = value
