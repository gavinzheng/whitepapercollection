# Copyright (C) 2017, Philsong <songbohr@gmail.com>

from ._viabtc import Viabtc

class Viabtc_BTC_CNY(Viabtc):
    def __init__(self):
        super().__init__("CNY", "BTC", "btccny")

