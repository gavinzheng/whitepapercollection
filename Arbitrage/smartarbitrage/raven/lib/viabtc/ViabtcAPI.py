# -*- coding:utf-8 -*-
# 这是对viabtd.com的API进行的封装。
# author: LucasPHBS
# update: 20170811

##
from __future__ import unicode_literals

# viabtc给出的请求demo和库，用于POST和DELETE请求
# https://github.com/viabtc/viabtc_exchange_cn_api_cn
from .oauth import RequestClient
##


# 交易系统函数集 ViabtcOrder
class ViabtcClient(object):
    # 初始化
    def __init__(self, acs_id, scr_key):
        self.access_id = acs_id
        self.secret_key = scr_key

    # 1. 查询账户信息
    def get_account(self):
        request_client = RequestClient(
                access_id=self.access_id,
                secret_key=self.secret_key
        )
        result = request_client.request('GET', 'https://www.viabtc.com/api/v1/balance/')
        return result.json()

    # 4. 获取订单状态
    def get_order_status(self, order_id, market="BCCCNY"):
        """

        :param order_id: 从订单中获取的一串数字信息
        :param market: 市场列表
        :return: order_status，形如：
            {
              "code": 0,
              "data": {                           # 订单数据
                "amount": "1000",                 # 委托数量
                "avg_price": "11782.28",          # 平均成交价格
                "create_time": 1496761108,        # 下单时间
                "deal_amount": "1000",            # 成交数量
                "deal_fee": "23564.5798468",      # 交易手续费用
                "deal_money": "11782289.9234",    # 成交金额
                "id": 300021,                     # 订单编号
                "left": "9.4",                    # 未成交数量
                "maker_fee_rate": "0.001",        # maker费率
                "market": "BTCCNY",               # 市场
                "order_type": "limit",            # 委托类型
                "price": "7000",                  # 委托价格
                "status": "done",                 # 订单状态
                "taker_fee_rate": "0.002",        # taker费率
                "type": "sell"                    # 订单类型
                }
              },
              "message": "Ok"
            }
        """
        request_client = RequestClient(
            access_id=self.access_id,
            secret_key=self.secret_key
        )

        data = {"id": str(order_id),
               "market": market}

        result = request_client.request(
            'GET',
            'https://www.viabtc.com/api/v1/order/',
            params=data,
        )
        return result.json()

    # 5. 下市价单
    def order_market(self, order_type, amount, market="BCCCNY"):
        """

        下市价单

        :param order_type: "buy" or "sell"
        :param amount: > 0.01               #市价单时，sell的amount是数量，buy的amount是金额。
        :param market: one from market list
        :return:
        {
          "code": 0,
          "data": {
            "amount": "56.5",              # 委托数量
            "avg_price": "11641.3",        # 平均成交价格
            "create_time": 1496798479,     # 下单时间
            "deal_amount": "56.5",         # 成交数量
            "deal_money": "657733.4561",   # 成交金额
            "id": 300032,                  # 订单编号
            "left": "0",                   # 未成交数量
            "maker_fee_rate": "0",         # maker手续费率
            "market": "BTCCNY",            # 市场
            "order_type": "market",        # 委托类型：limit:限价单；market:市价单；
            "price": "0",                  # 委托价格
            "source_id": "123",            # 用户自定义编号
            "status": "done",              # 订单状态：done:已成交；part_deal:部分成交；not_deal:未成交；
            "taker_fee_rate": "0.002",     # taker手续费率
            "type": "sell"                 # 订单类型：sell:卖出订单；buy:买入订单；
          },
          "message": "Ok"
        }
        """
        request_client = RequestClient(
            access_id=self.access_id,
            secret_key=self.secret_key
        )

        data = {
            "amount": str(amount),
            "type": order_type,
            "market": market
        }

        result = request_client.request(
            'POST',
            'https://www.viabtc.com/api/v1/order/market',
            json=data,
        )
        return result.json()

    # 6. 下限价单
    def order_limit(self, order_type, amount, price, market="BCCCNY"):
        """

        下限价单

        :param order_type: "buy" or "sell"
        :param amount: > 0.01               #限价单时，amount一直表示数量。
        :param price: > 0
        :param market: one from market list
        :return:
        {
          "code": 0,
          "data": {
            "amount": "56.5",              # 委托数量
            "avg_price": "11641.3",        # 平均成交价格
            "create_time": 1496798479,     # 下单时间
            "deal_amount": "56.5",         # 成交数量
            "deal_fee": "1315.4669122",    # 交易手续费用
            "deal_money": "657733.4561",   # 成交金额
            "id": 300032,                  # 订单编号
            "left": "0",                   # 未成交数量
            "maker_fee_rate": "0.001",     # maker手续费率
            "market": "BTCCNY",            # 市场
            "order_type": "limit",         # 委托类型：limit:限价单；market:市价单；
            "price": "7000",               # 委托价格
            "source_id": "123",            # 用户自定义编号
            "status": "done",              # 订单状态：done:已成交；part_deal:部分成交；not_deal:未成交；
            "taker_fee_rate": "0.002",     # taker手续费率
            "type": "sell"                 # 订单类型：sell:卖出订单；buy:买入订单；
          },
          "message": "Ok"
        }
        """
        request_client = RequestClient(
            access_id=self.access_id,
            secret_key=self.secret_key
        )

        data = {
            "amount": str(amount),
            "price": str(price),
            "type": order_type,
            "market": market
        }

        result = request_client.request(
            'POST',
            'https://www.viabtc.com/api/v1/order/limit',
            json=data,
        )
        return result.json()

    # 7. 撤销订单
    def cancel_order(self, order_id, market="BCCCNY"):
        """
        撤销订单
        :param order_id: 需要提前获取订单id
        :param market: 市场代码
        :return:
        {
          "code": 0,
          "data": {
            "amount": "56.5",              # 委托数量
            "avg_price": "11641.3",        # 平均成交价格
            "create_time": 1496798479,     # 下单时间
            "deal_amount": "56.5",         # 成交数量
            "deal_fee": "1315.4669122",    # 交易手续费用
            "deal_money": "657733.4561",   # 成交金额
            "id": 300032,                  # 订单编号
            "left": "0",                   # 未成交数量
            "maker_fee_rate": "0.001",     # maker手续费率
            "market": "BTCCNY",            # 市场
            "order_type": "limit",         # 委托类型：limit:限价单；market:市价单；
            "price": "7000",               # 委托价格
            "source_id": "123",            # 用户自定义编号
            "status": "done",              # 订单状态：done:已成交；part_deal:部分成交；not_deal:未成交；
            "taker_fee_rate": "0.002",     # taker手续费率
            "type": "sell"                 # 订单类型：sell:卖出订单；buy:买入订单；
          },
          "message": "Ok"
        }
        """
        request_client = RequestClient(
            access_id=self.access_id,
            secret_key=self.secret_key
        )

        data = {
            "order_id": str(order_id),
            "market": market
        }

        result = request_client.request(
            'DELETE',
            'https://www.viabtc.com/api/v1/order/pending',
            json=data,
        )

        return result.json()
