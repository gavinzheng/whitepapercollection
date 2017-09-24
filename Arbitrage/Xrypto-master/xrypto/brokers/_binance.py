# Copyright (C) 2017, Philsong <songbohr@gmail.com>

from .broker import Broker, TradeException
import config
import logging
from binance.client import Client
from binance.enums import *

class Binance(Broker):
    def __init__(self, base_currency, market_currency, pair_code, api_key=None, api_secret=None):
        super().__init__(base_currency, market_currency, pair_code)

        self.client = Client(
                    api_key if api_key else config.Binance_API_KEY,
                    api_secret if api_secret else config.Binance_SECRET_TOKEN)
 
    def _place_order(self, amount, price, side):
        order = client.create_order(
            symbol=self.pair_code,
            side=side,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=amount,
            price=str(price))
        logging.verbose('_place_order: %s %s' % (side, order))

        return order['orderId']

    def _buy_limit(self, amount, price):
        """Create a buy limit order"""
        return self._place_order(amount, price, SIDE_BUY)

    def _sell_limit(self, amount, price):
        """Create a sell limit order"""
        return self._place_order(amount, price, SIDE_SELL)

    def _order_status(self, res):
        resp = {}
        resp['order_id'] = res['orderId']
        resp['amount'] = float(res['origQty'])
        resp['price'] = float(res['price'])
        resp['deal_amount'] = float(res['executedQty'])
        resp['avg_price'] = float(res['price'])

        if res['status'] == ORDER_STATUS_NEW or res['status'] == ORDER_STATUS_PARTIALLY_FILLED:
            resp['status'] = 'OPEN'
        else:
            resp['status'] = 'CLOSE'

        return resp

    def _get_order(self, order_id):
        res = self.client.get_order(orderId=int(order_id), symbol=self.pair_code)
        logging.verbose('get_order: %s' % res)

        assert str(res['symbol']) == str(self.pair_code)
        assert str(res['orderId']) == str(order_id)
        return self._order_status(res['data'])

    def _cancel_order(self, order_id):
        res = self.client.cancel_order(orderId=int(order_id), symbol=self.pair_code)
        logging.verbose('cancel_order: %s' % res)

        assert str(res['orderId']) == str(order_id)
        return True

    def _get_balances(self):
        """Get balance"""
        res = self.client.get_account()
        logging.debug("get_balances: %s" % res)

        balances = res['balances']


        for entry in balances:
            currency = entry['asset'].upper()
            if currency not in (
                    'BTC', 'BCH', 'USD'):
                continue

            if currency == 'BCH':
                self.bch_available = float(entryfree['free'])
                self.bch_balance = float(entry['amount']) + float(entry['locked'])

            elif currency == 'BTC':
                self.btc_available = float(entry['free'])
                self.btc_balance = float(entry['amount']) + float(entry['locked'])
                
        return res
