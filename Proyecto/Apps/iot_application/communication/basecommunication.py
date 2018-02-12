

class BaseCommunication():

    client_id = None

    def __init__(self):
        pass

    def create_message(self, telemetry):
        return {"device_id": self.client_id, "telemetry": telemetry}
