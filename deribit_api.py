# -*- coding: utf-8 -*-

import time, hashlib, base64
import json
from collections import OrderedDict
from websocket import create_connection, WebSocketConnectionClosedException

class RestClient(object):
    def __init__(self, key=None, secret=None, url=None):
        self.key = key
        self.secret = secret

        if url:
            self.url = url
        else:
            self.url = "wss://www.deribit.com/ws/api/v2"


        self.auth_creds = {
              "jsonrpc" : "2.0",
              "id" : 0,
              "method" : "public/auth",
              "params" : {
                "grant_type" : "client_credentials",
                "client_id" : self.key,
                "client_secret" : self.secret
              }
            }

    def request(self, msg):
        auth_data = None
        try:
            ws = create_connection(self.url)
            if msg["method"].startswith("private/"):
                ws.send(json.dumps(self.auth_creds))
                while ws.connected:
                    auth_data = json.loads(ws.recv())
                    if "refresh_token" in auth_data["result"]:
                        pass
                    elif "error" in auth_data:
                        raise ValueError(auth_data, "issue in authorisation")
                    break
        except Exception as e:
            print(e)

        try:
            ws.send(json.dumps(msg))
            while ws.connected:
                data = json.loads(ws.recv())
                if "error" in data:
                    raise ValueError(data , "issue with loading api ")
                    break
                return data["result"]
        except Exception as e:
            print(e)

        return {"error"}




    def getorderbook(self, instrument, depth=5):
        msg = {}

        params = {
            "instrument_name": instrument,
            "depth": depth
        }
        msg["method"] = "public/get_order_book"
        msg["params"] = params

        return self.request(msg)


    def getcurrencies(self):

        return self.request("api/v2/public/get_currencies", {})


    def getlasttrades(self, instrument, count=None):
        options = {
            'instrument': instrument
        }

        if count:
            options['count'] = count

        return self.request("/api/v2/public/get_last_trades_by_instrument", options)


    def getsummary(self, currency="BTC"):
        return self.request("/api/v2/public/get_account_summary", {"currency": currency, "extended" : 'true'})


    def index(self, currency="BTC"):
        return self.request("/api/v2/public/get_index", {"currency": currency})

    # put a hidden option in
    def buy(self, instrument, quantity, price, postOnly=None, reduce_only=None, hidden=None, label=None):

        msg = {}

        params = {
            "instrument_name": instrument,
            "amount": quantity,
            "price": price
        }

        # and hidden will be a variable in signature of the function
        if hidden:
            params["hidden"] = 'true'
        if label:
            params["label"] = label

        if postOnly:
            params["post_only"] = 'true'

        if reduce_only:
            params["reduce_only"] = 'true'

        msg["method"] = "private/buy"
        msg["params"] = params

        return self.request(msg)

    # quantities are done in multiple of 10
    def sell(self, instrument, quantity, price, postOnly=None, reduce_only=None, hidden=None, label=None):
        msg = {}
        params = {
            "instrument_name": instrument,
            "amount": quantity,
            "price": price
        }

        # and hidden will be a variable in signature of the function
        if hidden:
            params["hidden"] = 'true'
        if label:
            params["label"] = label

        if postOnly:
            params["post_only"] = 'true'

        if reduce_only:
            params["reduce_only"] = 'true'

        msg["method"] = "private/sell"
        msg["params"] = params

        return self.request(msg)


    def cancel(self, orderId):
        msg = {}
        params = {
            "order_id": orderId
        }

        msg["method"] = "private/cancel"
        msg["params"] = params

        return self.request(msg)


    def cancelall(self, instrument="BTC-PERPETUAL", typeDef="all"):
        msg = {}
        params = {
            "type": typeDef,
            "instrument_name": instrument
        }

        msg = {}
        msg["method"] = "private/cancelall"
        msg["params"] = params

        return self.request(msg)


    def getopenorders(self, instrument):
        params = {}

        if instrument:
            params["instrument_name"] = instrument

        msg = {}
        msg["method"] = "private/get_open_orders_by_instrument"
        msg["params"] = params

        return self.request(msg)


    def position(self, instrument="BTC-PERPETUAL"):
        msg = {}
        params = {
            "instrument_name": instrument
        }
        msg["method"] = "private/get_position"
        msg["params"] = params

        return self.request(msg)


    def orderstate(self, orderId=None):
        params = {}
        if orderId:
            params["order_id"] = orderId

        msg = {}
        msg["method"] = "private/get_order_state"
        msg["params"] = params

        return self.request(msg)


