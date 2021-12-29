from decimal import Decimal

class Order():
    def __init__(self):
        self._lastOrder = None
        self.size = Decimal(0)
        self._oldOrder = None

    def setOrder(self, lastOrder):
        self._oldOrder = self._lastOrder
        self._lastOrder = lastOrder

    def getOldOrder(self):
        if (self._oldOrder != None):
            temp = Order()
            temp.setOrder(self._oldOrder)
            return temp
        return Order()

    def getCurrentOrder(self):
        return self._lastOrder

    def ifContains(self, item):
        if item in self._lastOrder:
            return True
        return False

    def setCoinSize(self, size):
        self._lastOrder['size'] = size

    def getCoinSize(self):
        return self._lastOrder['size']

    def getSize(self):
        return Decimal(self._lastOrder.get('quantity'))

    def setSize(self, size):
        self._lastOrder["quantity"] = size

    def getPrice(self):
        return Decimal(self._lastOrder.get('price'))

    def getId(self):
        return str(self._lastOrder.get('orderId'))

    def getSide(self):
        return self._lastOrder.get('direction')

    def isSideBuy(self):
        temp = self._lastOrder["direction"]
        return (temp == "Buy" or temp == "buy")

    def isSideSell(self):
        temp = self._lastOrder["direction"]
        return (temp == "Sell" or temp == "sell")

    def isOrderNone(self):
        if self._lastOrder == None:
            return True
        return False

    def getStatusIsRejected(self):
        if self._lastOrder.get('state') == 'Canceled':
            return True
        return False
