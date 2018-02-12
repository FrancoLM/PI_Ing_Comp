import random
import threading
import time
import json
import paho.mqtt.client as mqtt

from communication.basecommunication import BaseCommunication


class MQTTClient(BaseCommunication):

    SEND_TOPIC = "amq.topic.send.telemetry"
    RESPONSE_TOPIC = "amq.topic.response"

    _message_received = None

    @property
    def message_received(self):
        return self._message_received

    def __init__(self, host, port, username, password):

        self.host = host
        self.port = int(port)
        self.username = username
        self.password = password

        self.default_send_loop_time = 5
        self.default_keepalive = 60
        self.client_id = None

        self.client = mqtt.Client()
        self.client.username_pw_set(username=self.username, password=self.password)
        self.client.on_connect = self.on_connect
        # self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.connect(self.host, self.port, self.default_keepalive)

        t = threading.Thread(target=self.loop)
        t.start()

    def publish_message(self, message):
        self.client.publish(self.SEND_TOPIC, json.dumps(message))

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        self.client_id = client._client_id
        print("Client ID:", self.client_id)
        self.client.subscribe(self.RESPONSE_TOPIC)
        time.sleep(15)

    # The callback for when a PUBLISH message is received from the server.
    # Message received is sent to another queue, different from the one that device sends messages to.
    # queue name: mqtt-subscription-<device_id>qos<n>
    def on_message(self, client, userdata, msg):
        print("Received a message!")
        self.message_received = msg.payload
        print(msg.topic + " " + str(self.message_received))

    def on_subscribe(self, mosq, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def loop(self):
        self.client.loop_start()
        return
