#! /usr/bin/python
# -*- encoding: utf-8 -*-

# Copyright (C) 2017, Phil Song <songbohr@gmail.com>

import requests
import json
import time
import hashlib
import random
import hmac
import urllib
from collections import OrderedDict


class JubiAPI(object):
    def __init__(self, acs_id, scr_key):
        self.access_id = acs_id
        self.secret_key = scr_key
        self.base_url = 'https://www.jubi.com'

    def get_nonce(self):
        curr_stamp = time.time()*1000
        nonce = str(int(curr_stamp))
        return nonce

    def get_md5(self,s):
        m = hashlib.md5()
        m.update(s.encode())
        return m.hexdigest()

    def generate_signature(self, msg, secret_key):
        msg = msg.encode('utf-8')
        md5_hash = self.get_md5(secret_key)
        key = md5_hash.encode('utf-8')
        signature = hmac.new(key, msg, digestmod = hashlib.sha256).hexdigest()
        return signature

    def signature(self, params):
        if params is None:
            params = {}
        params['key'] = self.access_id
        params['nonce'] = self.get_nonce()
        orderDict = OrderedDict(params)
        param_str = urllib.parse.urlencode(orderDict)

        signature = self.generate_signature(param_str, self.secret_key)

        orderDict['signature'] = signature
        return orderDict

    def _get(self, url, params=None):
        result = requests.get(url, data=params)
        return result.json()  

    def _post(self, url, params=None):
        params = self.signature(params)
        result = requests.post(url, data=params)
        return result.json()  

    def get_ticker(self, coin):
        param = {'coin': coin}
        url = self.base_url + '/api/v1/ticker/'
        return self._get(url, param)

    def get_depth(self, coin):
        param = {'coin': coin}
        url = self.base_url + '/api/v1/depth/'
        return self._get(url, param)

    def get_orders(self, coin):
        param = {'coin': coin}
        url = self.base_url + '/api/v1/orders/'
        return self._get(url, param)

    def get_all_ticker(self):
        url = self.base_url + '/api/v1/allticker/'
        return self._get(url)

    def get_balances(self):
        url = self.base_url + '/api/v1/balance/'
        return self._post(url)

    def get_trades(self, coin):
        url = self.base_url + '/api/v1/trade_list/'
        params = {'coin': coin, 'type': 'all'}
        return self._post(url, params)

    def get_order(self, coin, trade_id):
        url = self.base_url + '/api/v1/trade_view/'
        params = {'coin': coin, 'id': trade_id}
        return self._post(url, params)

    def cancel_order(self, coin, trade_id):
        url = self.base_url + '/api/v1/trade_cancel/'
        params = {'coin': coin, 'id': trade_id}
        return self._post(url, params)

    def trade_add(self, coin, trade_type, amount, price):
        url = self.base_url + '/api/v1/trade_add/'
        params = { 'type': trade_type, 'coin': coin, 'amount': amount, 'price': price,}
        return self._post(url, params)

    def sell_limit(self, coin, amount, price):
        return self.trade_add(coin, "sell", amount, price)

    def buy_limit(self, coin, amount, price):
        return self.trade_add(coin, "buy", amount, price)

if __name__ == '__main__':
    Jubi_API_KEY = ''
    Jubi_SECRET_TOKEN = ''
    trader = JubiAPI(Jubi_API_KEY, Jubi_SECRET_TOKEN)
    # print(trader.get_ticker('btc'))
    # print(trader.get_depth('btc'))
    # print(trader.get_orders('btc'))
    # print(trader.get_all_ticker())

    # print(trader.get_balances())
    # print(trader.get_orders('eos'))
    print(trader.trade_add('eos', 'buy', 10, 1))
    print(trader.trade_add('eos', 'sell', 100, 10))

