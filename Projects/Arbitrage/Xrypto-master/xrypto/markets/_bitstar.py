# Copyright (C) 2017, Philsong <songbohr@gmail.com>

import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market

class Bitstar(Market):
    def __init__(self, pair_code):
        base_currency, market_currency = self.get_tradeable_pairs(pair_code)

        super().__init__(base_currency, market_currency, pair_code, 0.002)
        self.event = 'bitstar_depth'
        # self.subscribe_depth()

    def update_depth(self):
        url = 'https://www.bitstar.com/api/v1/market/depth/%s?size=50' % self.pair_code
        req = urllib.request.Request(url, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        res = urllib.request.urlopen(req)
        depth = json.loads(res.read().decode('utf8'))
        self.depth = self.format_depth(depth)

    def get_tradeable_pairs(self, pair_code):
        if pair_code == 'swap-btc-cny':
            base_currency = 'CNY'
            market_currency = 'BTC'
        else:
            assert(False)
        return base_currency, market_currency

# import urllib.request
# import urllib.error
# import urllib.parse
# import json
# from .market import Market
# import exchanges.bitstar_api as ApiClient

# class BS_StandardCNY(Market):
#     def __init__(self):
#         super().__init__('CNY')
#         self.update_rate = 1
#         self.client = ApiClient('', '')

#     def update_depth(self):
#         depth = {}
#         try:
#             publicinfo = self.client.publicinfo()
#             print(publicinfo)
#             depth['asks'] = [[publicinfo.standardprice, 1]]
#             depth['bids'] = [[publicinfo.standardprice, 1]]
#         except Exception as e:
#             return

#         self.depth = self.format_depth(depth)

