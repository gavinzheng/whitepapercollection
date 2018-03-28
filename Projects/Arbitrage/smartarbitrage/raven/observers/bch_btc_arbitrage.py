import logging
import config
import time
from .observer import Observer
from private_markets import bitfinex_bch_btc,bittrex_bch_btc
import os, time
import sys
import traceback
from .basicbot import BasicBot

class BCH_BTC_Arbitrage(BasicBot):
    def __init__(self):
        super().__init__()

        self.clients = {
            "Bitfinex_BCH_BTC": bitfinex_bch_btc.PrivateBitfinex_BCH_BTC(config.Bitfinex_API_KEY, config.Bitfinex_SECRET_TOKEN),
            "Bittrex_BCH_BTC": bittrex_bch_btc.PrivateBittrex_BCH_BTC(config.Bittrex_API_KEY, config.Bittrex_SECRET_TOKEN),
        }


        self.btc_profit_thresh = config.btc_profit_thresh
        self.btc_perc_thresh = config.btc_perc_thresh
        self.trade_wait = config.trade_wait  # in seconds
        self.last_trade = 0

        self.last_bid_price = 0
        self.trend_up = True

        logging.info('BCH_BTC_Arbitrage Setup complete')

    def begin_opportunity_finder(self, depths):
        self.potential_trades = []

        # Update client balance
        self.update_balance()

        self.check_order(depths)

    def update_balance(self):
        for kclient in self.clients:
            self.clients[kclient].get_balances()

    def end_opportunity_finder(self):
        if not self.potential_trades:
            return
        self.potential_trades.sort(key=lambda x: x[0])
        # Execute only the best (more profitable)
        self.execute_trade(*self.potential_trades[0][1:])

    def get_min_tradeable_volume(self, bprice, btc_bal, bch_bal):
        min1 = float(btc_bal)/bprice - config.bch_frozen_volume
        min2 = float(bch_bal)  - config.bch_frozen_volume

        return min(min1, min2)

    def check_order(self, depths):
        # update price

        # query orders
        if self.is_buying():
            buy_orders = self.get_orders('buy')
            buy_orders.sort(key=lambda x: x['price'], reverse=True)

            for buy_order in buy_orders:
                logging.debug(buy_order)
                result = self.clients[buy_order['market']].get_order(buy_order['id'])
                logging.debug (result)
                if not result:
                    logging.warn("get_order buy #%s failed" % (buy_order['id']))
                    continue

                if result['status'] == 'CLOSE' or result['status'] == 'CANCELED':
                    left_amount = result['amount'] - result['deal_size']
                    if  result['status'] == 'CANCELED' or left_amount > 0.001:
                        logging.info("cancel ok %s result['price'] = %s, left_amount=%s" % (buy_order['market'], result['price'], left_amount))
                        self.clients[buy_order['market']].buy_limit(left_amount, result['price']*(1+ 5*config.price_departure_perc))

                    self.remove_order(buy_order['id'])
                else:
                    try:
                        ask_price =  int(depths[buy_order['market']]["asks"][0]['price'])
                    except  Exception as ex:
                        logging.warn("exception depths:%s" % ex)
                        traceback.print_exc()
                        continue

                    if abs(result['price']-ask_price)/result['price'] > config.price_departure_perc:
                        print(result['price'], ask_price)
                        logging.info("%s %s" % (abs(result['price']-ask_price)/result['price'], config.price_departure_perc))
                        left_amount = result['amount'] - result['deal_size']
                        logging.info("Fire:cancel %s ask_price %s result['price'] = %s, left_amount=%s" % (buy_order['market'], ask_price, result['price'], left_amount))
                        self.cancel_order(buy_order['market'], 'buy', buy_order['id'])

        if self.is_selling():
            sell_orders = self.get_orders('sell')
            sell_orders.sort(key=lambda x: x['price'])

            for sell_order in self.get_orders('sell'):
                logging.debug(sell_order)
                result = self.clients[sell_order['market']].get_order(sell_order['id'])
                logging.debug (result)
                if not result:
                    logging.warn("get_order sell #%s failed" % (sell_order['id']))
                    continue

                if result['status'] == 'CLOSE' or result['status'] == 'CANCELED':
                    left_amount = result['amount'] - result['deal_size']
                    if result['status'] == 'CANCELED' or left_amount > 0.001:
                        logging.info("cancel ok %s result['price'] = %s, left_amount=%s" % (sell_order['market'], result['price'], left_amount))

                        self.clients[sell_order['market']].sell_limit(left_amount, result['price']*(1 - 5*config.price_departure_perc))

                    self.remove_order(sell_order['id'])
                else:
                    try:
                        bid_price = int(depths[sell_order['market']]["bids"][0]['price'])
                    except  Exception as ex:
                        logging.warn("exception depths:%s" % ex)
                        traceback.print_exc()
                        continue

                    if abs(result['price']-bid_price)/result['price'] > config.price_departure_perc:
                        left_amount = result['amount'] - result['deal_size']

                        logging.info("Fire:cancel %s bid_price %s result['price'] = %s,left_amount=%s" % (sell_order['market'], bid_price, result['price'], left_amount))
                        self.cancel_order(sell_order['market'], 'sell', sell_order['id'])

    def opportunity(self, profit, volume, bprice, kask, sprice, kbid, perc,
                    w_bprice, w_sprice, 
                    base_currency, market_currency):
        if kask not in self.clients:
            logging.warn("Can't automate this trade, client not available: %s" % kask)
            return
        if kbid not in self.clients:
            logging.warn("Can't automate this trade, client not available: %s" % kbid)
            return

        if self.buying_len() >= config.BUY_QUEUE:
            logging.warn("Can't automate this trade, BUY queue is full: %s" % self.buying_len())
            return

        if self.selling_len() >= config.SELL_QUEUE:
            logging.warn("Can't automate this trade, SELL queue is full: %s" % self.selling_len())
            return

        if profit > self.btc_profit_thresh and perc > self.btc_perc_thresh:
            logging.info("Profit or profit percentage(%0.4f/%0.4f%%) higher than thresholds(%s/%s%%)" 
                            % (profit, perc, self.btc_profit_thresh, self.btc_perc_thresh))    
        else:
            logging.debug("Profit or profit percentage(%0.4f/%0.4f) out of scope thresholds(%s/%s%%)" 
                            % (profit, perc, self.btc_profit_thresh, self.btc_perc_thresh))
            return

        if perc > 20:  # suspicous profit, added after discovering btc-central may send corrupted order book
            logging.warn("Profit=%f seems malformed" % (perc, ))
            return

        max_avaliable_volume = self.get_min_tradeable_volume(bprice,
                                                   self.clients[kask].btc_available,
                                                   self.clients[kbid].bch_avalibale)
        volume = min(volume, max_avaliable_volume)
        volume = min(volume, config.bch_max_tx_volume)

        if volume < config.bch_min_tx_volume:
            logging.warn("Can't automate this trade, minimum volume transaction"+
                         " not reached %f/%f" % (volume, config.bch_min_tx_volume))
            return

        current_time = time.time()
        if current_time - self.last_trade < self.trade_wait:
            logging.warn("Can't automate this trade, last trade " +
                         "occured %.2f seconds ago" %
                         (current_time - self.last_trade))
            return

        self.potential_trades.append([profit, volume, kask, kbid,
                                      w_bprice, w_sprice,
                                      bprice, sprice, base_currency, market_currency])

    def execute_trade(self, volume, kask, kbid, w_bprice,
                      w_sprice, bprice, sprice, base_currency, market_currency):
        volume = float('%0.2f' % volume)

        bch_frozen_volume = config.bch_frozen_volume

        if self.clients[kask].btc_available < max(volume*bprice, bch_frozen_volume*bprice):
            logging.warn("%s %s is insufficent" % (kask, base_currency))
            return
 
        if self.clients[kbid].bch_avalibale < max(volume, bch_frozen_volume):
            logging.warn("%s %s is insufficent" % (kbid, market_currency))
            return

        logging.info("Fire:Buy @%s/%0.4f and sell @%s/%0.4f %0.2f %s" % (kask, bprice, kbid, sprice, volume, market_currency))

        # update trend
        if self.last_bid_price < bprice:
            self.trend_up = True
        else:
            self.trend_up = False

        logging.info("trend is %s[%s->%s]", "up, buy then sell" if self.trend_up else "down, sell then buy", self.last_bid_price, bprice)
        self.last_bid_price = bprice
        self.last_trade = time.time()

        # trade
        if self.trend_up:
            result = self.new_order(kask, 'buy', maker_only=False, amount=volume, price=bprice)
            if not result:
                logging.warn("Buy @%s %f %s failed" % (kask, volume, market_currency))
                return


            result = self.new_order(kbid, 'sell', maker_only=False, amount=volume,  price=sprice)
            if not result:
                logging.warn("Sell @%s %f %s failed" % (kbid, volume, market_currency))
                result = self.new_order(kask, 'sell', maker_only=False, amount=volume, price=bprice)
                if not result:
                    logging.warn("2nd sell @%s %f %s failed" % (kask, volume, market_currency))
                    return
        else:

            result = self.new_order(kbid, 'sell', maker_only=False, amount=volume,  price=sprice)
            if not result:
                logging.warn("Sell @%s %f %s failed" % (kbid, volume, market_currency))
                return

            result = self.new_order(kask, 'buy', maker_only=False, amount=volume, price=bprice)
            if not result:
                logging.warn("Buy @%s %f %s failed" % (kask, volume, market_currency))
                result = self.new_order(kbid, 'buy', maker_only=False, amount= volume,  price=sprice)
                if not result:
                    logging.warn("2nd buy @%s %f %s failed" % (kbid, volume, market_currency))
                    return
        return

