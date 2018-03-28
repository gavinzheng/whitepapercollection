# Copyright (C) 2017, Philsong <songbohr@gmail.com>

import json
import config
from .market import Market
from exchanges.okcoin.OkcoinSpotAPI import OKCoinSpot

class OKCoin(Market):
    def __init__(self, pair_code):
        base_currency, market_currency = self.get_tradeable_pairs(pair_code)

        super().__init__(base_currency, market_currency, pair_code, 0.002)
        self.client = OKCoinSpot(None, None)
        self.event = 'okcoin_depth'
        self.subscribe_depth()

    def update_depth(self):
        raw_depth = self.client.depth(symbol=self.pair_code)
        self.depth = self.format_depth(raw_depth)

    def get_tradeable_pairs(self, pair_code):
        if pair_code == 'btc_cny':
            base_currency = 'CNY'
            market_currency = 'BTC'
        else:
            assert(False)
        return base_currency, market_currency