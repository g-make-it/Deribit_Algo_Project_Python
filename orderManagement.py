from order import Order
import time
from decimal import Decimal

class OrderManagement():
    def __init__(self):
        self._clientDERIBIT = None

    def run(self, clientMap):
        self._clientDERIBIT = clientMap["deribit"]

    def cancelAll(self):
        try:
            orders = self._clientDERIBIT.cancelall()
            print(str(orders) + " any outstanding orders are cancelled")
        except Exception as e:
            self.exceptionHandler(e, " error on cancelling all")

    def cancelOrder(self, orderObject):
        if not isinstance(orderObject, Order):
            return
        orderObjectCancelled = None
        try:
            orderObjectCancelled = self._clientDERIBIT.cancel(orderObject.getId())
            print("cancel order " + str(orderObjectCancelled))
        except Exception as e:
            self.exceptionHandler(e, " Cancelling order Error, trying again")
        return orderObjectCancelled

    def buyOrder(self, indiceName,size, price, reduce_only=False):
        try:

            lastOrderObject = self._clientDERIBIT.buy(instrument=indiceName, quantity=str(size),price=str(price),reduce_only=reduce_only, postOnly=True, hidden=True, label=None)["order"]
            print("Buy order sent - " + str(lastOrderObject))
            return lastOrderObject
        except Exception as e:
            self.exceptionHandler(e, " Error creating an order buy, exiting")
            return None

    def sellOrder(self, indiceName,size, price, reduce_only=False):
        # try using bulk orders to create these orders
        try:
            lastOrderObject = self._clientDERIBIT.sell(instrument=indiceName, quantity=str(size),price=str(price), reduce_only=reduce_only, postOnly=True, hidden=True, label=None)["order"]
            print("Sell order sent - " + str(lastOrderObject))
            return lastOrderObject
        except Exception as e:
            self.exceptionHandler(e, " Error creating an order sell, exiting")
            return None

    def orderStatus(self, listOfOrders, instrument):

        orderItem = None
        mapOfOutcomes = {"open":False ,"cancelled": False, "fullyFilled": False, "partFilled": False, "orderStatus": orderItem}

        while(True):
            try:
                orderMapList = self._clientDERIBIT.getopenorders(instrument=instrument)
                # orders from Deribit
                for order in orderMapList:
                    # order we have save from when we sent them
                    for localOrder in listOfOrders:

                        # some order may come back as a None due to the connection timing out
                        if localOrder == None or localOrder.isOrderNone():
                            continue

                        if order["order_id"] == localOrder.getId():
                            # print("order cancelled")
                            mapOfOutcomes["open"] = True
                            mapOfOutcomes["fullyFilled"] = False
                            return mapOfOutcomes
                        else:
                            mapOfOutcomes["fullyFilled"] = True
                return mapOfOutcomes

            except Exception as e:
                self.exceptionHandler(e, " order status function throw an error")


    def getOpenOrders(self, indiceName):
        while(True):
            try:
                orders = self._clientDERIBIT.getopenorders(instrument=indiceName)
                return orders
            except Exception as e:
                self.exceptionHandler(e, " getOpenOrders function throw an error")

    def exceptionHandler(self, e, task):
        print(str(e), " error occured when doing " + task)
        time.sleep(5)




