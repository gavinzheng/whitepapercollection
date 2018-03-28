# Copyright (C) 2017, Philsong <songbohr@gmail.com>

from ._viabtc import Viabtc

class Viabtc_BCH_BTC(Viabtc):
    def __init__(self):
        super().__init__("BTC", "BCH", "bccbtc")

if __name__ == "__main__":
    market = Viabtc_BCH_BTC()
    print(market.get_ticker())