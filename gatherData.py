from decimal import Decimal, ROUND_HALF_DOWN
import time
import math
from deribit_api import RestClient as DERIBITClassClient
from deribit_V2_API_Websocket import Deribitv2API
from threading import Thread
import json

class GatherData():
    def __init__(self):
        self.deribitWebSocket = Deribitv2API()
        self.previousQuoteString = ''

    def setting_url(self, map_client):
        url = map_client["url"]
        self.deribitWebSocket.setting_url(url)

    def start(self):
        # parsing a delegate to the thread for this function and then say to start the thread later on
        self.APIThread = Thread(target=self.deribitWebSocket.startSocket)
        self.APIThread.start()

    def run(self, clientMap):
        clientDERIBIT = clientMap["deribit"]
        if not (isinstance(clientDERIBIT, DERIBITClassClient)): return
        # get data and sort it and return none is the data is the same as before
        newQuote = self.sortData(self.deribitWebSocket.getListOfData())

        if newQuote == None: return None

        # newQuoteString = str(newQuote["bid"]) +  "-" +  str(newQuote["ask"])
        # # incase the quotes have not changed
        # if newQuoteString == self.previousQuoteString:
        #     return None
        # # setting the strings
        # self.previousQuoteString = newQuoteString

        # return the map of quotes
        return newQuote


    def errorFound(self,e):
        print(str(e) + " -+waiting for data so sleeping for 15s")
        time.sleep(15)
        return None

    def sortData(self, mapOfData):

        bestPrices = None

        if (mapOfData != None) and\
                "params" in mapOfData and "data" in mapOfData["params"] \
            and ("best_bid_price" in mapOfData['params']['data'] and "best_ask_price" in mapOfData['params']['data']):

            bestPrices = {"bid": Decimal(mapOfData['params']['data']['best_bid_price']),
                          "ask": Decimal(mapOfData['params']['data']['best_ask_price'])}
            bestPrices["mean"] = (bestPrices["bid"] + bestPrices["ask"])/Decimal(2)

        #     after map = json.loads(self.listOfNotifications[-1]) -> map['params']['data']['best_bid_price']
        # map['params']['data']['best_ask_price']

        return bestPrices
