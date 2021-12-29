from gatherData import GatherData
from generateSignals import GenerateSignals
from orderManagement import OrderManagement
from positionManagement import PositionManagement
from order import Order
from decimal import Decimal
import math


class AlgorithmScaling():
    def __init__(self):
        self.counterSinceOrderWasMade = 0
        self.orderManagementObject = None
        self.indiceName = "BTC-PERPETUAL"
        self.fundingAmount = 20
        # new tick size put in place
        self.differenceInPrice = Decimal(0.5)

        self.exitingOrder = False
        self.enteringOrder = False

        self.timeLimit = 30
        # these two below change base on how much money we have in our account
        self.numberOfScalingOrders = 24
        # the price difference between each order -- additional functionality added to increase spread
        self.priceMovementUnit = 2
        # used to multiple by the price to increase the spread
        self.rateOfChange = 12

        # turn into none
        self.orderManagementObject = None
        # turn into none      // trade cycles set to two
        self.numberOfTradeCyclesLimit = 200
        self.numberOfTradeCycles = 0

        self.emptyPosition = True

        self.orders = {"sell":[], "buy":[]}
        self.listOfMapOfOrdersExit = []
        self.listOfMapOfOrdersEnter = []

        self.exitingSize = 10



    def run(self, data, mapOfSignals, positionManagementObject,  orderManagementObject):

        if not isinstance(orderManagementObject, OrderManagement): return
        if not isinstance(positionManagementObject, PositionManagement): return

        self.orders = {"sell": [], "buy": []}
        self.orderManagementObject = orderManagementObject

        '''
        Order checking
        '''
        # check if orders are present for exiting
        mapOfOutcomesExit = self.orderPresent(listOfOrdersMaps=self.listOfMapOfOrdersExit, switchIfOrderIsPresent=self.exitingOrder)

        '''
        Order exit/enter order canceling
        '''
        # if all the exiting orders are filled then remove the entering orders
        if mapOfOutcomesExit["fullyFilled"]:

            # here check our position
            currentPositionStatus = positionManagementObject.findOurCurrentPosition()
            if (currentPositionStatus != None) and ("error" in currentPositionStatus): return
            self.emptyPosition = currentPositionStatus == None

            # exit order has been completed
            self.exitingOrder = False

            # if we still have no position right now then go ahead and exit all our orders that are resting
            if self.emptyPosition:
                self.removeAllOrdersAndResetFlags()
        '''
        Order exit/enter order canceling
        '''
        # check if orders are present for entering
        mapOfOutcomesEnter = self.orderPresent(listOfOrdersMaps=self.listOfMapOfOrdersEnter, switchIfOrderIsPresent=self.enteringOrder)
        '''
        Order checking and editing above the if statement
        '''


        '''
        Position checking
        '''
        currentPositionStatus = positionManagementObject.findOurCurrentPosition()
        if (currentPositionStatus != None) and ("error" in currentPositionStatus): return
        self.emptyPosition = currentPositionStatus == None

        mapOfExitSignals = {
            "buy" : False,
            "sell" : False
        }
        if currentPositionStatus != None:
            spread = data["ask"] - data["bid"]
            if currentPositionStatus["direction"] == "sell":
                if (data["ask"]+spread) < currentPositionStatus["average_price"]:
                    mapOfExitSignals["buy"] = True
            elif currentPositionStatus["direction"] == "buy":
                if (data["bid"]-spread) > currentPositionStatus["average_price"]:
                    mapOfExitSignals["sell"] = True
        '''
        Position checking
        '''

        '''
        Order checking
        '''

        '''
        Order exit order canceling
        '''
        self.counterSinceOrderWasMade += 1
        # check if we need to cancel anything
        if self.counterSinceOrderWasMade > self.timeLimit:
            # remove the exit positions cancel
            # if self.exitingOrder:
            self.cancelTakeOutPositionOrders()
            self.exitingOrder = False
            self.counterSinceOrderWasMade = 0

            '''
            The enter orders did not hit and the price moved away-------
            '''
            if self.emptyPosition:
                self.removeAllOrdersAndResetFlags()

        '''
        Order exit order canceling
        '''

        # remove the previous list of orders
        if len(self.listOfMapOfOrdersExit) > 2: del(self.listOfMapOfOrdersExit[0])
        if len(self.listOfMapOfOrdersEnter) > 2: del(self.listOfMapOfOrdersEnter[0])

        # if we find a buy signal and we are not in a position and we have not made any orders to enter
        intialStartBuy = mapOfSignals["buy"] and self.emptyPosition and (not self.enteringOrder)
        # if we find a buy signal and we are in a position and the position is a short and we have not made any orders to exit
        exitPositionBuy = mapOfExitSignals["buy"] and (not self.emptyPosition) and currentPositionStatus["direction"] == "sell" and (not self.exitingOrder)

        # if we find a sell signal and we are not in a position and we have not made any orders to enter
        intialStartSell = mapOfSignals["sell"] and self.emptyPosition and (not self.enteringOrder)
        # if we find a sell signal and we are in a position and the position is a long and we have not made any orders to exit
        exitPositionSell = mapOfExitSignals["sell"] and (not self.emptyPosition) and currentPositionStatus["direction"] == "buy" and (not self.exitingOrder)


        if intialStartBuy or intialStartSell:
            # check the number of trade cycles that have occurred
            self.exitClause()
            print("out of position entering both buy and sell orders")
            self.enterOrderScaling(side="buy", size=self.fundingAmount, price=data["bid"], listOfMapOrders=self.listOfMapOfOrdersEnter)
            self.enterOrderScaling(side="sell", size=self.fundingAmount, price=data["ask"], listOfMapOrders=self.listOfMapOfOrdersEnter)
            self.enteringOrder = True

            self.counterSinceOrderWasMade = 0

        elif exitPositionBuy or exitPositionSell:
            if exitPositionSell:
                # reverse the side as we are exiting the position
                print("in position")
                self.exitOrderScaling(side="sell", price=data["ask"], orderStatus=currentPositionStatus, listOfMapOrders=self.listOfMapOfOrdersExit)
                self.exitingOrder = True

            elif exitPositionBuy:
                # reverse the side as we are exiting the position
                print("in position")
                self.exitOrderScaling(side="buy", price=data["bid"], orderStatus=currentPositionStatus, listOfMapOrders=self.listOfMapOfOrdersExit)
                self.exitingOrder = True

            self.counterSinceOrderWasMade = 0



    # -----------------------when entering an order we have times our sizes by 10 to increase the size but the price distribution is still the same
    def enterOrderScaling(self, side, size, price, listOfMapOrders):
        newPrice = price
        newSize = size

        for counter in range(self.numberOfScalingOrders):
            if side == "buy":
                deribitOrderObject=self.orderManagementObject.buyOrder(indiceName=self.indiceName, size= newSize ,price=newPrice)
                self.createACustomOrderObject(orderList=self.orders["buy"], order=deribitOrderObject)
                # new functionality orders are scaled up but not exponentially
                rateOfScalingOrders = self.rateOfChange * counter
                newPrice= newPrice - (self.priceMovementUnit + rateOfScalingOrders)
                # new functionality orders are scaled up but not exponentially

            elif side == "sell":
                deribitOrderObject = self.orderManagementObject.sellOrder(indiceName=self.indiceName, size= newSize , price=newPrice)
                self.createACustomOrderObject(orderList=self.orders["sell"], order=deribitOrderObject)
                # new functionality orders are scaled up but not exponentially
                rateOfScalingOrders = self.rateOfChange * counter
                newPrice = newPrice + (self.priceMovementUnit + rateOfScalingOrders)
                # new functionality orders are scaled up but not exponentially

        listOfMapOrders.append(self.orders)




    def exitOrderScaling(self, side, price, orderStatus, listOfMapOrders):
        newPrice = price
        newSize = self.exitingSize
        numberOrders = int(abs(orderStatus["size"])/newSize)

        for counter in range(numberOrders):

            if side == "buy":
                deribitOrderObject=self.orderManagementObject.buyOrder(indiceName=self.indiceName, size=newSize,price=newPrice, reduce_only=True)
                self.createACustomOrderObject(orderList=self.orders["buy"], order=deribitOrderObject)
                # newPrice -= self.differenceInPrice
                newPrice = newPrice - self.differenceInPrice
            elif side == "sell":
                deribitOrderObject = self.orderManagementObject.sellOrder(indiceName=self.indiceName, size=newSize, price=newPrice, reduce_only=True)
                self.createACustomOrderObject(orderList=self.orders["sell"], order=deribitOrderObject)
                # newPrice += self.differenceInPrice
                newPrice = newPrice + self.differenceInPrice


        listOfMapOrders.append(self.orders)


    def orderPresent(self, listOfOrdersMaps, switchIfOrderIsPresent):

        mapOfStatus = {"open": True, "fullyFilled": True}
        # if it is false then we can deduce that there are no orders present, however if true we only work out what orders are still
        if switchIfOrderIsPresent:
            listOfOrders = listOfOrdersMaps[-1]["sell"] if listOfOrdersMaps[-1]["sell"] else listOfOrdersMaps[-1]["buy"]

            outcome = self.orderManagementObject.orderStatus(listOfOrders=listOfOrders, instrument=self.indiceName)
            if outcome["open"] or outcome["partFilled"]:
                mapOfStatus = {"open": True, "fullyFilled": False}
                return mapOfStatus

            # assume that cancelled and fullyFilled will be True and that works for what we have
            mapOfStatus = {"open": False, "fullyFilled": True}
            return mapOfStatus
        return {"open": False, "fullyFilled":False}


    def createACustomOrderObject(self, orderList, order):
        customOrder = Order()
        if order == None:
            return
        customOrder.setOrder(order)
        orderList.append(customOrder)


    def cancelTakeOutPositionOrders(self):
        # print("canceling exit position orders")
        listOfOrders = self.orderManagementObject.getOpenOrders(self.indiceName)
        for order in listOfOrders:
            if order["amount"] == (self.exitingSize):
                # takes in a custom order object
                orderObject = Order()
                orderObject.setOrder(order)
                self.orderManagementObject.cancelOrder(orderObject=orderObject)

    def removeAllOrdersAndResetFlags(self):
        self.orderManagementObject.cancelAll()
        # as there are no orders so they can't be in one
        self.exitingOrder = False
        self.enteringOrder = False




    def exitClause(self):
        self.numberOfTradeCycles += 1
        if self.numberOfTradeCycles >= self.numberOfTradeCyclesLimit:
            print("end program")
            exit(0)
