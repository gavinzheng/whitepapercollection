# Copyright (C) 2017, Philsong <songbohr@gmail.com>

from ._viabtc import Viabtc

class Viabtc_BCH_CNY(Viabtc):
    def __init__(self):
        super().__init__("CNY", "BCH", "bcccny")

if __name__ == "__main__":
    market = Viabtc_BCH_CNY()
    print(market.get_ticker())