# Copyright (C) 2017, Philsong <songbohr@gmail.com>

import logging
import requests
from .market import Market
from binance.client import Client


class Binance(Market):
    def __init__(self, pair_code):
        base_currency, market_currency = self.get_tradeable_pairs(pair_code)

        super().__init__(base_currency, market_currency, pair_code, 0.001)

        self.client = Client(None, None)

    def update_depth(self):
        raw_depth = self.client.get_order_book(symbol=self.pair_code)
        self.depth = self.format_depth(raw_depth)

    def get_tradeable_pairs(self, pair_code):
        if pair_code == 'ETHBTC':
            base_currency = 'BTC'
            market_currency = 'ETH'
        elif pair_code == 'BNBBTC':
            base_currency = 'BTC'
            market_currency = 'BNB'
        elif pair_code == 'BNBETH':
            base_currency = 'ETH'
            market_currency = 'BNB'
        elif pair_code == 'MCOBTC':
            base_currency = 'BTC'
            market_currency = 'MCO'
        elif pair_code == 'MCOETH':
            base_currency = 'ETH'
            market_currency = 'MCO'
        elif pair_code == 'QTUMBTC':
            base_currency = 'BTC'
            market_currency = 'QTUMBCH'
        elif pair_code == 'QTUMETH':
            base_currency = 'ETH'
            market_currency = 'QTUM'
        elif pair_code == 'WTCBTC':
            base_currency = 'BTC'
            market_currency = 'WTC'
        elif pair_code == 'WTCETH':
            base_currency = 'ETH'
            market_currency = 'WTC'
        else:
            assert(False)
        return base_currency, market_currency