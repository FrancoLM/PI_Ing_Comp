# Import RPi -> composition
import time
import RPi.GPIO as GPIO
from gpio.basegpio import BaseGPIO


class RaspberryPi3GPIO(BaseGPIO):

    RPi_LOW = GPIO.LOW
    RPi_HIGH =GPIO.HIGH

    def __init__(self, protocol, address, port, username, password):
        super().__init__(protocol, address, port, username, password)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        time.sleep(2)

    def setup_input_gpio(self, pin_number):
        GPIO.setup(pin_number, GPIO.IN)
        self.input_gpio.append(pin_number)

    def setup_output_gpio(self, pin_number):
        GPIO.setup(pin_number, GPIO.OUT)
        self.output_gpio.append(pin_number)

    def get_input_value(self, pin_number):
        # TODO: check if the requested pin was set by the application
        return GPIO.input(pin_number)

    def set_output_value(self, pin_number, value):
        GPIO.output(pin_number, value)
