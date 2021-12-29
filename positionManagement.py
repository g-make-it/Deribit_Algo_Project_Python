class PositionManagement():
    def __init__(self):
        self._clientDERIBIT = None
        self.currentPosition = None
        self.indiceName = "BTC-PERPETUAL"

    def setClients(self, clientMap):
        self._clientDERIBIT = clientMap["deribit"]

    def findOurCurrentPosition(self):
        try:
            #result = self._clientDERIBIT.getorderbook(instrument=self.indiceName, depth=5)
            #result = self._clientDERIBIT.getinstruments(currency="BTC", doesExpire=False, kind="future")
            currentPosition = self._clientDERIBIT.position(self.indiceName)
            if currentPosition == None:
                return None
            if currentPosition["size"] == 0:
                return None
            else:
                return currentPosition
        except Exception as e:
            print(str(e) + " error occured in the position management class")
            return {"error"}

