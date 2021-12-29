from websocket import create_connection, WebSocketConnectionClosedException
import json
import time

class Deribitv2API():

    def __init__(self):
        self.msg = \
            {"jsonrpc": "2.0",
             "method": "public/subscribe",
             "id": 42,
             "params": {
                "channels": ["quote.BTC-PERPETUAL"]}
            }

        self.listOfNotifications = []
        self.ws = None
        self.url = None

    def setting_url(self, url):
        self.url = url

    def startSocket(self):
        # try again after a failure
        while True:
            try:
                self.connect()
                self.listen()
            except Exception as e:
                self.endSocketDueToError(e)


    def connect(self):
        self.ws = create_connection(self.url)
        self.ws.send(json.dumps(self.msg))

    def listen(self):
        # trigger whilst true keep listening
        while self.ws.connected:
            try:
                # puts all the incoming data into a list of a map
                mapData = json.loads(self.ws.recv())
                self.listOfNotifications.append(mapData)
            except Exception as e:
                self.endSocketDueToError(e)
                return

    def disconnect(self):
        try:
            if self.ws.connected:
                self.ws.close()
        except WebSocketConnectionClosedException as e:
            print(str(e) + " error on  closing")
        print("Socket Closed")
    # send the data to the logicalEngine

    def endSocketDueToError(self, e):
        print(e, " closing websocket")
        self.disconnect()

    def getListOfData(self):
        if len(self.listOfNotifications) > 1:
            self.listOfNotifications = self.listOfNotifications[-2:]
            # returns the last value in the list
            return self.listOfNotifications[-1]
        # since we have no data don't return anything
        return None
