import urllib2
import json

from .auth import Auth
BASE_URL = 'https://yunbi.com'

API_BASE_PATH = '/api/v2'
API_PATH_DICT = {
    # GET
    'members': '%s/members/me.json',
    'markets': '%s/markets.json',

    #market code required in url as {market}.json
    'tickers' : '%s/tickers/%%s.json',
    #market required in url query string as '?market={market}'
    'orders': '%s/orders.json',

    #order id required in url query string as '?id={id}'
    'order': '%s/order.json',

    #market required in url query string as '?market={market}'
    'order_book': '%s/order_book.json',

    #market required in url query string as '?market={market}'
    'trades': '%s/trades.json',

    #market required in url query string as '?market={market}'
    'my_trades': '%s/trades/my.json',

    'k': '%s/k.json',
    #clear orders in all markets
    'clear': '%s/orders/clear.json',

    #delete a specific order
    'delete_order': '%s/order/delete.json',

    #TODO multi orders API
    'multi_orders': '%s/orders/multi.json',
}

def get_api_path(name):
    # type: (object) -> object
    path_pattern = API_PATH_DICT[name]
    return path_pattern % API_BASE_PATH

class YunbiClient():

    def __init__(self, access_key=None, secret_key=None):
        if access_key and secret_key:
            self.auth = Auth(access_key, secret_key)
        else:
            from conf import ACCESS_KEY, SECRET_KEY
            self.auth = Auth(ACCESS_KEY, SECRET_KEY)


    def get(self, path, params=None, is_public_api=False):
        verb = "GET"
        if is_public_api:
            url = "%s%s" % (BASE_URL, path)
        else:
            signature, query = self.auth.sign_params(verb, path, params)
            url = "%s%s?%s&signature=%s" % (BASE_URL, path, query, signature)
       
        print url
        print verb

        resp = urllib2.urlopen(url)
        data = resp.readlines()
        if len(data):
            return json.loads(data[0])


    def post(self, path, params=None):
        verb = "POST"
        print params
        signature, query = self.auth.sign_params(verb, path, params)
        url = "%s%s" % (BASE_URL, path)
        data = "%s&signature=%s" % (query, signature)
        print url
        print verb
        print data

        resp = urllib2.urlopen(url, data)
        data = resp.readlines()
        if len(data):
            return json.loads(data[0])

    def get_depth(self, market):
        params = {"market": market}
        return self.get(get_api_path('order_book'), params)

    def get_balance(self):
        return self.get(get_api_path('members'))

    def get_order(self, order_id):
        params = {"id": order_id}
        return self.get(get_api_path('order'), params)

    def cancel_order(self, order_id):
        params = {"id": order_id}
        return self.post(get_api_path('delete_order'), params)

    def _place_order(self, market, side, amount, price):
        params = {'market': market, 'side': side, 'volume': amount, 'price': price, 'ord_type': 'limit'}
        return self.post(get_api_path('orders'), params)

    def sell_limit(self, market, amount, price):
        return self._place_order(market, "sell", amount, price)

    def buy_limit(self, market, amount, price):
        return self._place_order(market, "buy", amount, price)
