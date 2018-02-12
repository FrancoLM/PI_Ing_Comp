from communication.communicationclient import CommunicationClient


class BaseGPIO():

    _pin_value = None
    _input_gpio = []
    _output_gpio = []

    @property
    def value(self):
        return self._pin_value

    @property
    def input_gpio(self):
        return self._input_gpio

    @property
    def output_gpio(self):
        return self._output_gpio

    def __init__(self, protocol, host, port, username, password):
        # setup mqtt
        self.communication_client = CommunicationClient.create(protocol, host, port, username, password)

    def setup_input_gpio(self, pin_number):
        raise NotImplementedError

    def setup_output_gpio(self, pin_number):
        raise NotImplementedError

    def get_input_value(self):
        raise NotImplementedError

    def set_output_value(self, value):
        raise NotImplementedError
