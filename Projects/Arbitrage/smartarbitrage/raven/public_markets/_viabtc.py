# Copyright (C) 2017, Philsong <songbohr@gmail.com>

import logging
import requests
from .market import Market

# https://www.viabtc.com/api/v1/market/depth?market=bcccny&limit=1&merge=0

# {
#   "code": 0,
#   "data": {
#     "asks": [
#       [
#         "3355",
#         "0.5851"
#       ]
#     ],
#     "bids": [
#       [
#         "3352",
#         "0.6"
#       ]
#     ]
#   },
#   "message": "Ok"
# }

class Viabtc(Market):
    def __init__(self, base_currency, market_currency, pair_code):
        super().__init__(base_currency, market_currency, pair_code, 0.002)

    def update_depth(self):
        url = 'https://www.viabtc.com/api/v1/market/depth?market=%s&merge=0' % self.pair_code
        response = requests.request("GET", url, timeout=self.request_timeout)
        raw_depth = response.json()

        self.depth = self.format_depth(raw_depth)

    # override method
    def format_depth(self, depth):
        bids = self.sort_and_format(depth['data']['bids'], True)
        asks = self.sort_and_format(depth['data']['asks'], False)
        return {'asks': asks, 'bids': bids}
