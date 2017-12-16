# Copyright (C) 2017, Phil Song <songbohr@gmail.com>

# python3 xrypto/cli.py -m Viabtc_BCH_CNY,Viabtc_BCH_BTC,Viabtc_BTC_CNY t-watch -v
import logging
import time
import config
from .basicbot import BasicBot
from brokers.broker_factory import create_brokers

class TrigangularArbitrer_Binance(BasicBot):
    def __init__(self, base_pair, pair1, pair2, monitor_only=True):
        super().__init__()
        self.base_pair = base_pair
        self.pair_1 = pair1
        self.pair_2 = pair2

        self.tFee = config.TFEE

        self.monitor_only = monitor_only

        self.max_trade_amount = 100

        t_api_key = config.t_Binance_API_KEY
        t_secret_token = config.t_Binance_SECRET_TOKEN

        # self.clients = {
        #     self.base_pair: viabtc_bch_cny.BrokerViabtc_BCH_CNY(t_api_key, t_secret_token),
        #     self.pair_1: viabtc_bch_btc.BrokerViabtc_BCH_BTC(t_api_key, t_secret_token),
        #     self.pair_2: viabtc_btc_cny.BrokerViabtc_BTC_CNY(t_api_key, t_secret_token),
        # }

        self.last_trade = 0

    def update_balance(self):
        pass
        # self.clients[self.base_pair].get_balances()

    def tick(self, depths):
        self.forward(depths)
        # self.reverse()


    def forward(self, depths):
        base_pair_ask_amount = depths[self.base_pair]["asks"][0]["amount"]
        base_pair_ask_price = depths[self.base_pair]["asks"][0]["price"]

        logging.verbose("base_pair: %s ask_price:%s"% (self.base_pair, base_pair_ask_price))

        pair1_bid_amount = depths[self.pair_1]["bids"][0]["amount"]
        pair1_bid_price = depths[self.pair_1]["bids"][0]["price"]

        pair2_bid_amount = depths[self.pair_2]["bids"][0]["amount"]
        pair2_bid_price = depths[self.pair_2]["bids"][0]["price"]

        if pair1_bid_price == 0:
            return

        pair_2to1_bch_amount = pair2_bid_amount/pair1_bid_price
        # print(pair2_bid_amount, pair1_bid_price, pair_2to1_bch_amount)

        max_trade_amount = self.max_trade_amount
        hedge_bch_amount = min(base_pair_ask_amount, pair1_bid_amount)
        hedge_bch_amount = min(hedge_bch_amount, pair_2to1_bch_amount)
        hedge_bch_amount = min(max_trade_amount, hedge_bch_amount)

        if hedge_bch_amount < 0.05:
            logging.verbose('hedge_ bch _amount is too small! %s' % hedge_bch_amount)
            return

        hedge_btc_amount = hedge_bch_amount*pair1_bid_price
        if hedge_btc_amount < 0.001:
            logging.verbose('hedge_ btc _amount is too small! %s' % hedge_btc_amount)
            return

        synthetic_bid_price = round(pair1_bid_price*pair2_bid_price, 8)

        t_price = round(base_pair_ask_price*self.tFee*config.Diff, 8)
        logging.verbose("synthetic_bid_price: %s t_price:%s" % (synthetic_bid_price, t_price))

        p_diff = synthetic_bid_price - t_price
        profit = p_diff*hedge_bch_amount

        if profit > 0:
            logging.info('profit=%0.8f, p_diff=%0.8f, amount=%s' % (profit, p_diff, hedge_bch_amount))
            logging.info("synthetic_bid_price: %s  base_pair_ask_price: %s t_price: %s" % (
                synthetic_bid_price, 
                base_pair_ask_price,
                t_price))

            logging.info('buy %s @%s, sell BTC @synthetic: %s' % (self.base_pair, hedge_bch_amount, hedge_btc_amount))
            
            if profit < 0.0005:
                logging.warn('profit should >= 0.0005 BTC')
                return

            current_time = time.time()
            if current_time - self.last_trade < 5:
                logging.warn("Can't automate this trade, last trade " +
                             "occured %.2f seconds ago" %
                             (current_time - self.last_trade))
                return
            
            if not self.monitor_only:
                pass
                # self.clients[self.base_pair].buy_limit(hedge_bch_amount, base_pair_ask_price)
                # self.clients[self.pair_1].sell_limit(hedge_bch_amount, pair1_bid_price)
                # self.clients[self.pair_2].sell_limit(hedge_btc_amount, pair2_bid_price)

            self.last_trade = time.time()


    def reverse(self):
        print("t3 reverse:")

        base_pair_bid_amount = depths[self.base_pair]["bids"][0]["amount"]
        base_pair_bid_price = depths[self.base_pair]["bids"][0]["price"]

        logging.verbose("base_pair: %s bid_price:%s"% (self.base_pair, base_pair_bid_price))

        pair1_ask_amount = depths[self.pair_1]["asks"][0]["amount"]
        pair1_ask_price = depths[self.pair_1]["asks"][0]["price"]

        pair2_ask_amount = depths[self.pair_2]["asks"][0]["amount"]
        pair2_ask_price = depths[self.pair_2]["asks"][0]["price"]

        if pair1_ask_price == 0  or pair2_ask_price == 0:
            return

        pair_2to1_bch_amount = pair2_ask_amount/pair1_ask_price
        # print(pair2_bid_amount, pair1_bid_price, pair_2to1_bch_amount)

        max_trade_amount = 0.1
        hedge_bch_amount = min(base_pair_bid_amount, pair1_ask_amount)
        hedge_bch_amount = min(hedge_bch_amount, pair_2to1_bch_amount)
        hedge_bch_amount = min(max_trade_amount, hedge_bch_amount)

        if hedge_bch_amount < 0.05:
            logging.verbose('hedge_ bch _amount is too small! %s' % hedge_bch_amount)
            return

        hedge_btc_amount = hedge_bch_amount*pair1_ask_price
        if hedge_btc_amount < 0.01:
            logging.verbose('hedge_ btc _amount is too small! %s' % hedge_btc_amount)
            return

        synthetic_ask_price = round(pair1_ask_price*pair2_ask_price, 2)

        t_price = round(base_pair_bid_price*config.TFEE*config.Diff, 2)
        logging.verbose("synthetic_ask_price: %s t_price:%s" % (synthetic_ask_price, t_price))

        p_diff = synthetic_ask_price - t_price

        profit = round(p_diff*hedge_bch_amount, 2)
        logging.verbose('profit=%s' % profit)

        if p_diff > 0:
            logging.verbose("find t!!!: p_diff:%s synthetic_ask_price: %s  base_pair_bid_price: %s t_price: %s" % (
                p_diff,
                synthetic_ask_price, 
                base_pair_bid_price,
                t_price))

            logging.verbose('r--sell %s BCH @%s, buy @synthetic: %s' % (self.base_pair, hedge_bch_amount, hedge_btc_amount))
            

            current_time = time.time()
            if current_time - self.last_trade < 10:
                logging.warn("Can't automate this trade, last trade " +
                             "occured %.2f seconds ago" %
                             (current_time - self.last_trade))
                return


            self.clients[self.base_pair].sell_limit(hedge_bch_amount, base_pair_bid_price)
            self.clients[self.pair_2].buy_limit(hedge_btc_amount, pair2_ask_price)
            self.clients[self.pair_1].buy_limit(hedge_bch_amount, pair1_ask_price)

            self.last_trade = time.time()



