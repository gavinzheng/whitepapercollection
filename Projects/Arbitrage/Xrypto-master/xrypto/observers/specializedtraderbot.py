import logging
import config
import time
from .observer import Observer
from brokers import haobtccny,huobicny,okcoincny

from .emailer import send_email


class SpecializedTraderBot(Observer):
    def __init__(self):
        self.haobtc = haobtccny.BrokerHaobtcCNY(config.HAOBTC_API_KEY, config.HAOBTC_SECRET_TOKEN)

        self.okcoin = okcoincny.BrokerOkCoinCNY(config.OKCOIN_API_KEY, config.OKCOIN_SECRET_TOKEN)

        self.brokers = {
            "HaobtcCNY": self.haobtc,
            "OkCoinCNY": self.okcoin,
        }
        self.profit_percentage_thresholds = {  # Graph
            "HaobtcCNY": {"OkCoinCNY": 3.5},
            "OkCoinCNY": {"HaobtcCNY": 1},
        }
        self.trade_wait = 60 * 5  # in seconds
        self.last_trade = 0
        self.potential_trades = []

    def begin_opportunity_finder(self, depths):
        self.potential_trades = []

    def end_opportunity_finder(self):
        if not self.potential_trades:
            return
        self.potential_trades.sort(key=lambda x: x[0])
        # Execute only the best (more profitable)
        self.execute_trade(*self.potential_trades[0][1:])

    def get_min_tradeable_volume(self, bprice, cny_bal, btc_bal):
        min1 = float(cny_bal) / ((1. + config.balance_margin) * bprice)
        min2 = float(btc_bal) / (1. + config.balance_margin)
        return min(min1, min2) * 0.95

    def opportunity(self, profit, volume, bprice, kask, sprice, kbid, perc,
                    w_bprice, w_sprice):
        if kask not in self.brokers:
            logging.warn(
                "Can't automate this trade, client not available: %s" % (kask))
            return
        if kbid not in self.brokers:
            logging.warn(
                "Can't automate this trade, client not available: %s" % (kbid))
            return
        if perc < self.profit_percentage_thresholds[kask][kbid]:
            logging.warn("Can't automate this trade, profit=%f is lower than defined threshold %f"
                         % (perc, self.profit_percentage_thresholds[kask][kbid]))
            return

        if perc > 20:  # suspicous profit, added after discovering btc-central may send corrupted order book
            logging.warn("Profit=%f seems malformed" % (perc, ))
            return

        # Update client balance
        self.update_balance()

        # maximum volume transaction with current balances
        max_volume = self.get_min_tradeable_volume(
            bprice, self.brokers[kask].cny_balance,
            self.brokers[kbid].btc_balance)
        volume = min(volume, max_volume, config.max_tx_volume)
        if volume < config.min_tx_volume:
            logging.warn("Can't automate this trade, minimum volume transaction not reached %f/%f" % (volume, config.min_tx_volume))
            logging.info("Balance on %s: %f CNY - Balance on %s: %f BTC" % (kask, self.brokers[kask].cny_balance, kbid, self.brokers[kbid].btc_balance))
            return

        current_time = time.time()
        if current_time - self.last_trade < self.trade_wait:
            logging.warn("Can't automate this trade, last trade occured %s seconds ago"
                         % (current_time - self.last_trade))
            return

        self.potential_trades.append([profit, volume, kask, kbid, w_bprice,
                                      w_sprice])

    def execute_trade(self, volume, kask, kbid, w_bprice, w_sprice):
        self.last_trade = time.time()
        logging.info("Buy @%s %f BTC and sell @%s" % (kask, volume, kbid))
        send_email("Bought @%s %f BTC and sold @%s" % (kask, volume, kbid),
                   "w_bprice=%f w_sprice=%f" % (w_bprice, w_sprice))
        self.brokers[kask].buy(volume)
        self.brokers[kbid].sell(volume)
