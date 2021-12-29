from orderManagement import OrderManagement
from decimal import Decimal
import math

class GenerateSignals():
    def __init__(self):
        # it means that the list will hold upto 30 minutes of data
        self.indexLimitForLists = 30

        self.incrementOverPeriodToCount = 0
        self.limitToExitPosition = Decimal(80)



    def run(self, mapOfData, positionStatus, orderManagementObject):
        # changed it from the close price of previous trades to the best quotes
        meanPriceFromQuotes = mapOfData["mean"]

        tempMap = {"close": meanPriceFromQuotes}
        mapOfSignals = self.generateSignal(tempMap)

        signalToSell = mapOfSignals["sell"]
        signalToBuy = mapOfSignals["buy"]

        #  stop exit if order is below average price
        if positionStatus != None:
            enteredPrice = Decimal(positionStatus['average_price'])
            # shorting - if the price we entered is smaller then what we want to exit with then stop - we want sell high buy low
            if positionStatus['direction'] == "sell":
                if meanPriceFromQuotes > (enteredPrice):
                    # print("price is too high turn signalToBuy to false")
                    signalToBuy = False
            # long - if the price we entered is larger then what we want to exit with then stop - we want sell high buy low
            elif positionStatus['direction'] == "buy":
                if meanPriceFromQuotes < (enteredPrice):
                    # print("price is too low turn signalToSell to false")
                    signalToSell = False



        '''
        Could be more simple but testing so keep separate other wise integrate with whats above if block
        '''
        # exit as soon as you surpass average price
        if positionStatus != None:
            enteredPrice = Decimal(positionStatus['average_price'])

            if positionStatus['direction'] == "sell":
                if meanPriceFromQuotes < (enteredPrice):
                    signalToBuy = True

            elif positionStatus['direction'] == "buy":
                if meanPriceFromQuotes > (enteredPrice):
                    signalToSell = True
        # exit as soon as you surpass average price

        """
        hints at possible loses
        """

        # exit order quickly
        if positionStatus != None:

            enteredPrice = Decimal(positionStatus['average_price'])
            # shorting
            if positionStatus['direction'] == "sell":
                if meanPriceFromQuotes > (enteredPrice + self.limitToExitPosition):
                    '''
                    if orders of the same position are still there then we do not send out a emergency signal
                    but RETURNS TRUE IF ORDER IS PRESENT
                    '''
                    signalToBuy = not self.checkIfAnyOrdersAreStillPresent(positionStatus, orderManagementObject)

                    if signalToBuy:
                        print("buy out, Lossing sell")

            # long
            elif positionStatus['direction'] == "buy":
                if meanPriceFromQuotes < (enteredPrice - self.limitToExitPosition):
                    '''
                    RETURNS TRUE IF ORDER IS PRESENT
                    '''
                    signalToSell = not self.checkIfAnyOrdersAreStillPresent(positionStatus, orderManagementObject)

                    if signalToSell:
                        print("sell out, Lossing buy")

        return {"sell": signalToSell, "buy": signalToBuy}

    # checks if orders are present on our current position thus moving the average price in our favour
    def checkIfAnyOrdersAreStillPresent(self, positionStatus, orderManagementObject):
        listOfPresentOrders = orderManagementObject.getOpenOrders(indiceName="BTC-PERPETUAL")
        # no orders present
        if len(listOfPresentOrders) == 0: return False
        if positionStatus != None:
            # going short
            if positionStatus['direction'] == "sell":
                # returns true if order is present
                return self.findItemByLoopingThroughPresentOrders(listOfPresentOrders, "sell")
            elif positionStatus['direction'] == "buy":
                return self.findItemByLoopingThroughPresentOrders(listOfPresentOrders, "buy")

    # finds if we still have orders on the same side as the position as it could fill later on increase/decreasing our average price
    def findItemByLoopingThroughPresentOrders(self, listOfOrders, side):
        for order in listOfOrders:
            if order["direction"] == side:
                return True
        return False

    # this means we are always going to enter orders, as the signal is always true
    def generateSignal(self, mapOfDataPrice):

        buySignal = True
        sellSignal = True

        return {"sell": sellSignal, "buy": buySignal}