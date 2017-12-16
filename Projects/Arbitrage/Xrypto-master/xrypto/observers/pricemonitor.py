import logging
from .observer import Observer
import json
import time
import os
import math
import random
import sys
import traceback
import config
from .basicbot import BasicBot
import threading
import requests

class PriceMonitor(Observer):
    out_dir = './data/'
    last_diff = 0
    last_cross_diff = 0
    okv_f = 'okv_diff6.csv'
    bv_f = 'bv_diff6.csv'

    def __init__(self):
        super().__init__()
        self.Viabtc_BTC_CNY = 'Viabtc_BTC_CNY'
        self.OKEx_Future_Quarter = 'OKEx_Future_Quarter'
        self.Bitfinex_BTC_USD = 'Bitfinex_BTC_USD'

        self.rate = self.get_exchange_rate()

    def get_exchange_rate(self):
        response = requests.request("GET", 'https://www.okex.com/api/v1/exchange_rate.do', timeout=10)
        exchange_rate = response.json()
        return exchange_rate['rate']

    def tick(self, depths):
        try:
            self.rate = self.get_exchange_rate()

            OKEx_Future_Quarter_bid = (depths[self.OKEx_Future_Quarter]["bids"][0]['price'])
            Viabtc_BTC_CNY_ask = (depths[self.Viabtc_BTC_CNY]["asks"][0]['price'])
            Viabtc_BTC_CNY_bid = (depths[self.Viabtc_BTC_CNY]["bids"][0]['price'])
            Bitfinex_BTC_USD_ask = depths[self.Bitfinex_BTC_USD]["asks"][0]['price']        
        except Exception as e:
            logging.error("ex:%s" % e)
            return
        
        diff = int(OKEx_Future_Quarter_bid*self.rate - Viabtc_BTC_CNY_ask)
        cross_diff = int(Bitfinex_BTC_USD_ask*self.rate - Viabtc_BTC_CNY_bid)

        if self.last_diff != diff:
            self.last_diff = diff
            self.save_to_csv(self.okv_f, Viabtc_BTC_CNY_ask, OKEx_Future_Quarter_bid*self.rate, diff)
            self.render_to_html()

        if self.last_cross_diff != cross_diff:
            self.last_cross_diff = cross_diff
            self.save_to_csv(self.bv_f, Viabtc_BTC_CNY_bid, Bitfinex_BTC_USD_ask*self.rate, cross_diff)
            self.render_to_html_cross()

        logging.info("rate=%s, viadiff=%s, bitfinex_diff=%s" % (self.rate, diff, cross_diff))


        return

    def save_to_csv(self, filename, p1, p2, diff):
        filename = self.out_dir + filename

        need_header = False
        if not os.path.exists(filename):
            need_header = True

        fp = open(filename, 'a+')

        if need_header:
            fp.write("timestamp, strtime, p1, p2, diff\n")

        timestr = time.strftime("%d/%m/%Y %H:%M:%S")

        fp.write(("%d") % time.time()+','+("%s") % timestr +','+("%.2f") % p1 +','+("%.2f") % p2 +','+("%.2f") % diff +'\n')
        fp.close()

    def render_to_html(self):
        import pandas as pd
        from pyecharts import Line

        df = pd.read_csv(self.out_dir + self.okv_f)

        attr = [i[1] for i in df.values]
        p1 = [i[2] for i in df.values]
        p2 = [i[3] for i in df.values]
        d3 = [i[4] for i in df.values]

        line = Line("统计套利")
        line.add("viabtc,okex期现价差", attr, d3, is_smooth=True, mark_point=["max","average","min"], mark_line=["max", "average","min"])
        # line.add("外盘内盘价差", attr2, v2, is_smooth=True, mark_line=["max", "average"])
        line.render('./data/index.html')

        line = Line("统计套利")
        line.add("via", attr, p1)
        line.add("ok季度", attr, p2)
        line.render('./data/index2.html')

    def render_to_html_cross(self):
        import pandas as pd
        from pyecharts import Line

        # df = pd.read_csv('./data/diff.csv')
        df = pd.read_csv(self.out_dir + self.bv_f)

        attr = [i[1] for i in df.values]
        p1 = [i[2] for i in df.values]
        p2 = [i[3] for i in df.values]
        d3 = [i[4] for i in df.values]

        line = Line("统计套利")
        line.add("via,bitfinex价差", attr, d3, is_smooth=True, mark_point=["max","average","min"], mark_line=["max", "average","min"])
        line.render('./data/c.html')

        line = Line("统计套利")
        line.add("via", attr, p1)
        line.add("bitfinex", attr, p2)
        line.render('./data/c2.html')