import argparse
import json
import time
import os
from pathlib import Path

from configobj import ConfigObj

from gpio import IoTDevice


class IoTApplication():

    LOOP_TIME = 5 # seconds
    MAX_DISTANCE = 0.4 # mts

    def __init__(self, args):
        # setup logging

        # read config file
        file_path = os.path.join("settings", "settings.cfg")
        self.device_settings = ConfigObj(file_path)
        # cfg_file['Protocol']['username'] = hbase

        address = self.device_settings['Login']['address']
        port = self.device_settings['Login']['port']
        username = self.device_settings['Login']['username']
        password = self.device_settings['Login']['password']

        # setup device
        self.device = IoTDevice.create(args.device, args.protocol, address, port, username, password)

        # Override the "on_message" callback
        self.device.communication_client.client.on_message = self.operate_leds

        # setup sensors and actuators
        self.distance_echo = self.device_settings['Device'].as_int('input_echo')
        self.device.setup_input_gpio(pin_number=self.distance_echo)
        self.distance_trig = self.device_settings['Device'].as_int('output_trig')
        self.device.setup_output_gpio(pin_number=self.distance_trig)

        output_leds = [int(led) for led in self.device_settings['Device']['output_leds']]
        for pin_output in output_leds:
            self.device.setup_output_gpio(pin_number=pin_output)

        # send values
        print("Initializing device...")
        time.sleep(17)
        print("Initialization Done!")
        time.sleep(3)

    def start_loop(self):
        # read value
        # create message
        # send message
        # TODO: cambiar todo en send_telemetry_loop
        try:
            while True:
                telemetry_value = self.get_telemetry_from_distance_sensor()
                message = self.device.communication_client.create_message(telemetry_value)
                self.device.communication_client.publish_message(message)
                time.sleep(self.LOOP_TIME)

        except KeyboardInterrupt:
            print("Program Ended")
            # TODO: cleanup. turn leds off

    def get_telemetry_from_distance_sensor(self):
        self.device.set_output_value(self.distance_trig, False)
        self.device.set_output_value(self.distance_trig, True)
        time.sleep(10 * 10 ** -6)  # 10 microseconds
        self.device.set_output_value(self.distance_trig, False)

        # Flank from 0 to 1 = start
        while self.device.get_input_value(self.distance_echo) == self.device.RPi_LOW:
            start = time.time()
        # Flank from 1 to 0 = end
        while self.device.get_input_value(self.distance_echo) == self.device.RPi_HIGH:
            end = time.time()

        time_measured = end - start
        return time_measured

    # on_message callback override
    def operate_leds(self, client, userdata, msg):

        print("Message returned by the system: " + msg.payload.decode("utf-8"))
        distance = json.loads(msg.payload.decode("utf-8"))['distance']  # float

        print("distance calculated by the system: '{message}' mts".format(message=distance))

        output_count = len(self.device.output_gpio)
        step = self.MAX_DISTANCE / output_count

        for i in range(output_count):
            if distance >= step * i:
                state = self.device.RPi_HIGH
            else:
                state = self.device.RPi_LOW
            self.device.set_output_value(self.device.output_gpio[i], state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='IoT Application')
    parser.add_argument('--device', type=str, help='IoT Device Type: "Emulator", "RaspberryPi3"', default="Emulator", required=False)
    parser.add_argument('--protocol', type=str, help='IoT Device Communication Protocol', default="MQTT", required=False)
    args = parser.parse_args()

    app = IoTApplication(args)
    app.start_loop()
