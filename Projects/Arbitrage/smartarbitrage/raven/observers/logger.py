import logging
import config
from .observer import Observer


class Logger(Observer):
    def opportunity(self, profit, volume, bprice, kask, sprice, kbid, perc,
                    w_bprice, w_sprice,
                    base_currency, market_currency):
        if profit > config.btc_profit_thresh and perc > config.btc_perc_thresh:
            logging.info("profit: %f %s with volume: %f %s - buy at %.8f (%s) sell at %.8f (%s) ~%.2f%%" \
                % (profit, base_currency, volume, market_currency, bprice, kask, sprice, kbid, perc))
