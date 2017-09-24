# Copyright (C) 2017, Philsong <songbohr@gmail.com>

from .broker import Broker, TradeException
import config
import logging
from exchanges.huobi_api import Client

class Huobi(Broker):
    def __init__(self, base_currency, market_currency, pair_code, api_key=None, api_secret=None):
        super().__init__(base_currency, market_currency, pair_code)

        if (market_currency != 'BTC' and  market_currency != 'LTC'):
            assert(False)
         
        if (base_currency != 'CNY'):
            assert(False)

        self.client = Client(
                    api_key if api_key else config.HUOBI_API_KEY,
                    api_secret if api_secret else config.HUOBI_SECRET_TOKEN)
 
    def _buy_limit(self, amount, price):
        """Create a buy limit order"""
        res = self.client.buy_limit(
            amount=str(amount),
            price=str(price),
            coin_type=self.market_currency.lower())

        logging.verbose('_buy_limit: %s' % res)

        return res['order_id']

    def _sell_limit(self, amount, price):
        """Create a sell limit order"""
        res = self.client.sell_limit(
            amount=str(amount),
            price=str(price),
            coin_type=self.market_currency.lower())
        logging.verbose('_sell_limit: %s' % res)

        return res['order_id']

    def _order_status(self, res):
        resp = {}

        resp['order_id'] = res['id']
        resp['amount'] = float(res['order_amount'])
        resp['price'] = float(res['order_price'])
        resp['deal_amount'] = float(res['processed_amount'])
        resp['avg_price'] = float(res['processed_price'])

        status = res['status']
        if status == 3 or status == 6:
            resp['status'] = 'CANCELED'
        elif status == 2:
            resp['status'] = 'CLOSE'
        else:
            resp['status'] = 'OPEN'
        return resp

    def _get_order(self, order_id):
        res = self.client.get_order_info(int(order_id), 
                                        coin_type=self.market_currency.lower())
        logging.verbose('get_order: %s' % res)

        assert str(res['orders'][0]['order_id']) == str(order_id)
        return self._order_status(res['orders'][0])

    def _get_orders(self, order_ids):
        raise
        orders = []
        res = self.client.get_orders(order_ids) 

        for order in res['orders']:
            resp_order = self._order_status(order)
            orders.append(resp_order)
                  
        return orders

    def _cancel_order(self, order_id):
        res = self.client.cancel_order(int(order_id), coin_type=self.market_currency.lower())
        logging.verbose('cancel_order: %s' % res)

        assert str(res['order_id']) == str(order_id)

        return True

    def _get_balances(self):
        """Get balance"""
        res = self.client.get_account_info()
        logging.debug("get_account_info: %s" % res)

        self.btc_available = float(res["available_btc_display"])
        self.cny_available = float(res["available_cny_display"])
        self.btc_frozen = float(res["frozen_btc_display"])
        self.cny_frozen = float(res["frozen_cny_display"])
        self.btc_balance = self.btc_available + self.btc_frozen
        self.cny_balance = self.cny_available + self.cny_frozen

        logging.debug(self)
        return res

    def _get_orders_history(self):
        raise
        orders = []
        res = self.client.get_orders_history(self.pair_code, pageLength=200)    
        for order in res['orders']:
            resp_order = self._order_status(order)
            orders.append(resp_order)
                  
        return orders