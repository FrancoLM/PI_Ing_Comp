from communication.mqttclient import MQTTClient

COMMUNICATION_PROTOCOL = {"MQTT": MQTTClient}

class CommunicationClient():

    @classmethod
    def create(cls, protocol, host, port, username, password):
        return COMMUNICATION_PROTOCOL[protocol](host, port, username, password)
