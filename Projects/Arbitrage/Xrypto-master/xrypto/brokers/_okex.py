# Copyright (C) 2017, Philsong <songbohr@gmail.com>

from .broker import Broker, TradeException
import config
import logging
from exchanges.okcoin.OkcoinFutureAPI import OKCoinFuture

class OKEx(Broker):
    def __init__(self, base_currency, market_currency, pair_code, api_key=None, api_secret=None):
        super().__init__(base_currency, market_currency, pair_code)

        self.client = OKCoinFuture(
                    api_key if api_key else config.OKEX_API_KEY,
                    api_secret if api_secret else config.OKEX_SECRET_TOKEN)
 
    def _buy_limit(self, amount, price):
        """Create a buy limit order"""
        res = self.client.buy_limit(
            symbol=self.pair_code,
            amount=str(amount),
            price=str(price))

        logging.verbose('_buy_limit: %s' % res)

        return res['order_id']

    def _sell_limit(self, amount, price):
        """Create a sell limit order"""
        res = self.client.sell_limit(
            symbol=self.pair_code,
            amount=str(amount),
            price=str(price))
        logging.verbose('_sell_limit: %s' % res)

        return res['order_id']

    def _order_status(self, res):
        resp = {}
        resp['order_id'] = res['order_id']
        resp['amount'] = float(res['amount'])
        resp['price'] = float(res['price'])
        resp['deal_amount'] = float(res['deal_amount'])
        resp['avg_price'] = float(res['avg_price'])
        resp['type'] = res['type']

        if res['status'] == 0 or res['status'] == 1 or res['status'] == 4:
            resp['status'] = 'OPEN'
        else:
            resp['status'] = 'CLOSE'

        return resp

    def _get_order(self, order_id):
        res = self.client.order_info(self.pair_code, int(order_id))
        logging.verbose('get_order: %s' % res)

        assert str(res['orders'][0]['order_id']) == str(order_id)
        return self._order_status(res['orders'][0])

    def _get_orders(self, order_ids):
        raise
        orders = []
        res = self.client.orders_info(self.pair_code, order_ids) 

        for order in res['orders']:
            resp_order = self._order_status(order)
            orders.append(resp_order)
                  
        return orders

    def _cancel_order(self, order_id):
        res = self.client.cancel_order(self.pair_code, int(order_id))
        logging.verbose('cancel_order: %s' % res)

        assert str(res['order_id']) == str(order_id)

        return True

    def _get_balances(self):
        """Get balance"""
        res = self.client.future_userinfo()
        logging.debug("future_userinfo: %s" % res)

        entry = res['info']['btc']

        self.btc_available = round(float(entry['account_rights']) - float(entry['keep_deposit']), 8)
        self.btc_balance = float(entry['account_rights'])

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