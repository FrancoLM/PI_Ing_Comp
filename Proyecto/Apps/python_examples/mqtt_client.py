# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import threading
import time


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client_id = client._client_id
    print("Client ID:", client_id)
    # I can make each client subscribe to an exchange given by their Client ID
    client.subscribe("device_exchange")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("control")


# The callback for when a PUBLISH message is received from the server.
# Message received is sent to another queue, different from the one that device sends messages to.
# queue name: mqtt-subscription-<device_id>qos<n>
# queue name: mqtt-subscription-paho/53DF1A9952D1483DFAqos0
def on_message(client, userdata, msg):
    print("Received a message!")
    print(msg.topic + " " + str(msg.payload))


def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def loop():
    client.loop_start()
    return

client = mqtt.Client()
# User name is vhost:username
client.username_pw_set(username='device_vhost:device_user', password='tesis1234')
# client.username_pw_set(username='admin', password='admin')
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect("127.0.0.1", 11883, 60)

t = threading.Thread(target=loop)
t.start()

while True:
    print("data published!")
    # client.publish("amq.topic/temp/mine", 22)
    # amq.topic is REQUIRED!
    client.publish("amq.topic.send.telemetry", 22)
    time.sleep(4)
