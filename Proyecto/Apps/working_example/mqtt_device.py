# -*- coding: utf-8 -*-
import random

import paho.mqtt.client as mqtt
import threading
import time
import json


class MQTT_Device():

    default_send_loop_time = 5

    def __init__(self):
        self.client_id = None
        self.client = mqtt.Client()
        # User name is vhost:username
        # self.client.username_pw_set(username='device_vhost:device_user', password='tesis1234')
        self.client.username_pw_set(username='device_user', password='tesis1234')
        # client.username_pw_set(username='admin', password='admin')
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.connect("18.231.98.175", 1883, 60)


        # time.sleep(30)
        # # Send registration message
        # message = self.create_message("Registration message")
        # self.client.publish("amq.topic.send.telemetry", json.dumps(message))

        t = threading.Thread(target=self.loop)
        t.start()

        # self.send_telemetry_loop()


    def send_telemetry_loop(self):
        while True:
            # amq.topic is REQUIRED!
            telemetry_value = random.uniform(0, 100)
            message = self.create_message(telemetry_value)
            print("Sending telemetry = {telemetry}".format(telemetry=telemetry_value) )
            self.client.publish("amq.topic.send.telemetry", json.dumps(message))
            time.sleep(self.default_send_loop_time)


    def create_message(self, telemetry):
        return {"device_id": self.client_id, "telemetry": telemetry}

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        self.client_id = client._client_id
        print("Client ID:", self.client_id)
        # I can make each client subscribe to an exchange given by their Client ID
        self.client.subscribe("amq.topic.response")
        # responses_deviceID_paho
       #  self.client.subscribe("paho." + self.client_id)
        time.sleep(15)

    # The callback for when a PUBLISH message is received from the server.
    # Message received is sent to another queue, different from the one that device sends messages to.
    # queue name: mqtt-subscription-<device_id>qos<n>
    def on_message(self, client, userdata, msg):
        print("Message returned by the system: " + msg.topic + " " + str(msg.payload))


    def on_subscribe(self, mosq, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def loop(self):
        self.client.loop_start()
        return


if __name__ == "__main__":
    mqtt_device = MQTT_Device()
    # Device needs to wait for its queue to be up and ready for messages
    time.sleep(20)
    mqtt_device.send_telemetry_loop()
