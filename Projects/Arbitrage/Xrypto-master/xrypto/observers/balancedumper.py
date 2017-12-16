from .observer import Observer
import json
import time
import os
from brokers import okex_btc_future,okcoin_btc_cny,huobi_btc_cny
import sys
import traceback
import config
import logging
from exchanges.emailer import send_email
from .basicbot import BasicBot

class BalanceDumper(BasicBot):
    exchange = 'OKCoin_BTC_CNY'
    last_profit = 0

    out_dir = './data/'
    profit_csv = 'profit.csv'

    def __init__(self):        
        self.brokers = {
            "OKEx_BTC_Future": okex_btc_future.BrokerOKEx_BTC_Future(config.OKEX_API_KEY, config.OKEX_SECRET_TOKEN),
            "OKCoin_BTC_CNY": okcoin_btc_cny.BrokerOKCoin_BTC_CNY(config.OKCOIN_API_KEY, config.OKCOIN_SECRET_TOKEN),
            "Huobi_BTC_CNY": huobi_btc_cny.BrokerHuobi_BTC_CNY(config.HUOBI_API_KEY, config.HUOBI_SECRET_TOKEN),
        }

        self.cny_balance = 0
        self.btc_balance = 0
        self.cny_frozen = 0
        self.btc_frozen = 0
        self.cny_total = 0
        self.btc_total = 0
       
        self.init_btc = 80
        self.init_cny = 2000000

        try:
            os.mkdir(self.out_dir)
        except:
            pass

    def save_profit(self, price, cny, btc, profit):
        filename = self.out_dir + self.profit_csv
        need_header = False

        if not os.path.exists(filename):
            need_header = True

        fp = open(filename, 'a+')

        timestr = time.strftime("%d/%m/%Y %H:%M:%S")

        if need_header:
            fp.write("timestamp, timestr, price, cny, btc, profit\n")
        line = "%d, %s, %.f, %.2f, %.6f, %.2f\n" % (time.time(), timestr, price, cny, btc, profit)
        fp.write(line)
        fp.close()

    def sum_balance(self):
        self.cny_balance = self.btc_balance = 0
        for kclient in self.brokers:
            self.cny_balance += self.brokers[kclient].cny_balance
            self.btc_balance += self.brokers[kclient].btc_balance

    def tick(self, depths):
        # Update client balance
        self.update_balance()
        self.sum_balance()

        # get price
        try:
            bid_price = int(depths[self.exchange]["bids"][0]['price'])
            ask_price = int(depths[self.exchange]["asks"][0]['price'])
        except  Exception as ex:
            logging.warn("exception depths:%s" % ex)
            traceback.print_exc()
            return

        if bid_price == 0 or ask_price == 0:
            logging.warn("exception ticker")
            return
        
        btc_diff = self.btc_balance - self.init_btc
        cny_diff = self.cny_balance - self.init_cny

        profit = btc_diff * bid_price + cny_diff

        logging.info('cny profit:%.2f', profit)

        if (abs(profit - self.last_profit) > 200):
            self.last_profit = profit
            self.save_profit(bid_price, 
                self.cny_balance, self.btc_balance,
                profit)
            self.render_to_html()

    def render_to_html(self):
        import pandas as pd
        from pyecharts import Line

        df = pd.read_csv(self.out_dir + self.profit_csv)

        attr = [i[1] for i in df.values]
        p1 = [i[2] for i in df.values]
        p2 = [i[3] for i in df.values]
        d3 = [i[4] for i in df.values]
        profit = [i[5] for i in df.values]

        line = Line("统计套利")
        line.add("profit", attr, profit, is_smooth=True, mark_point=["max","average","min"], mark_line=["max", "average","min"])
        # line.add("外盘内盘价差", attr2, v2, is_smooth=True, mark_line=["max", "average"])
        line.render('./data/p.html')
