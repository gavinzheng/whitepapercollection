# Copyright (C) 2016, Philsong <songbohr@gmail.com>

import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market
from exchanges.huobi_api import Client

class Huobi(Market):
    def __init__(self, pair_code):
        base_currency, market_currency = self.get_tradeable_pairs(pair_code)

        super().__init__(base_currency, market_currency, pair_code, 0.002)

        self.client = Client()

        self.event = 'huobi_depth'
        self.subscribe_depth()

    def update_depth(self):
        raw_depth = self.client.get_depth(currency=self.base_currency.lower(), coin_type=self.market_currency.lower(), count=50)
        self.depth = self.format_depth(raw_depth)

    def get_tradeable_pairs(self, pair_code):
        if pair_code == 'btc_cny':
            base_currency = 'CNY'
            market_currency = 'BTC'
        else:
            assert(False)
        return base_currency, market_currency
