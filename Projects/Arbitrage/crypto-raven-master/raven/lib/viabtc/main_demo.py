##
# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from ViabtcAPI import ViabtcOrder as Order
from ViabtcAPI import ViabtcData as Data
from TradeTools import DataStore as DS
import time
##
# 记录我的ID和KEY
access_id = "*******"
secret_key = "***************"
##

def refresh_and_restore_candles():
    DS.refresh_data_in_all_markets()


def roll_market_depth():
    try:
        while 1:
            print Data.get_market_depth(limit=1)
            time.sleep(0.25)
    except:
        roll_market_depth()

#
# if __name__ == "__main__":
#     while 1:  # 出问题后已经会自动刷新了，不需要重写自动刷新业务
#         refresh_and_restore_candles()
#         print "######################################## "
#         time.sleep(1800)


def pull_down(step=0.01, amount=0.01):
    order = Order(access_id, secret_key)
    last_id = ""
    last_price = 0
    while 1:
        time.sleep(0.5)
        print "0"
        market_depth = Data.get_market_depth(limit=1)
        bid_price, bid_amount = map(float, market_depth["data"]["bids"][0])
        ask_price, ask_amount = map(float, market_depth["data"]["asks"][0])

        # 先写一个追踪策略
        if ask_price > bid_price + step:
            if last_id != "":
                print "1"
                order.order_withdraw(last_id)
                if last_price <= bid_price + step:
                    print "4"
                    break
                sell1 = order.order_limit("sell",
                                         price=min([ask_price, last_price]) - step,
                                         amount=amount)
                print sell1
                last_id = sell1["data"]["id"]
                last_price = float(sell1["data"]["price"])
            else:
                print "2"
                sell1 = order.order_limit("sell",
                                         price=ask_price - step,
                                         amount=amount)
                print sell1
                last_id = sell1["data"]["id"]
                last_price = float(sell1["data"]["price"])
        else:
            print "3"
            order.withdraw_all()
            break


def pull_up(step=0.01, amount=0.01):
    order = Order(access_id, secret_key)
    last_id = ""
    last_price = 0
    while 1:
        time.sleep(0.5)
        print "0"
        market_depth = Data.get_market_depth(limit=1)
        bid_price, bid_amount = map(float, market_depth["data"]["bids"][0])
        ask_price, ask_amount = map(float, market_depth["data"]["asks"][0])

        # 先写一个追踪策略
        if ask_price > bid_price + step:
            if last_id != "":
                print "1"
                order.order_withdraw(last_id)
                if last_price + step >= ask_price:
                    print "4"
                    break
                buy1 = order.order_limit("buy",
                                         price=max([bid_price, last_price]) + step,
                                         amount=amount)
                print buy1
                last_id = buy1["data"]["id"]
                last_price = float(buy1["data"]["price"])
            else:
                print "2"
                buy1 = order.order_limit("buy",
                                         price=bid_price + step,
                                         amount=amount)
                print buy1
                last_id = buy1["data"]["id"]
                last_price = float(buy1["data"]["price"])
        else:
            print "3"
            order.withdraw_all()
            break


def clean_bid(level=1):
    order = Order(access_id, secret_key)
    market_depth = Data.get_market_depth()
    asks = market_depth["data"]["asks"][:level]
    bids = market_depth["data"]["bids"][:level]
    for i in bids:
        order.order_limit("sell", float(i[1]), float(i[0]))


def clean_ask(level=1):
    order = Order(access_id, secret_key)
    market_depth = Data.get_market_depth()
    asks = market_depth["data"]["asks"][:level]
    bids = market_depth["data"]["bids"][:level]
    for i in asks:
        order.order_limit("buy", float(i[1]), float(i[0]))


def top_bid(amount=0.01):
    order = Order(access_id, secret_key)

    market_depth = Data.get_market_depth(limit=1)
    bid_price, bid_amount = map(float, market_depth["data"]["bids"][0])
    ask_price, ask_amount = map(float, market_depth["data"]["asks"][0])

    od = order.order_limit("buy", amount=amount, price=ask_price-0.01)
    od_price = float(od["data"]["price"])
    od_id = od["data"]["id"]

    time.sleep(2)

    market_depth = Data.get_market_depth(limit=5)
    bid_price1, bid_amount1 = map(float, market_depth["data"]["bids"][0])
    ask_price1, ask_amount1 = map(float, market_depth["data"]["asks"][0])
    bid_price2, bid_amount2 = map(float, market_depth["data"]["bids"][1])
    ask_price2, ask_amount2 = map(float, market_depth["data"]["asks"][1])

    if bid_price1 != od_price:
        print "Shit, the deal has been eaten."
    else:
        if bid_amount1 != amount or bid_price2 == od_price - 0.01:
            print "There is a follower, let's crush him!"
            order.order_withdraw(order_id=od_id)
        else:
            print "There is no follower, peace."
            order.order_withdraw(order_id=od_id)


def self_deal(price, amount=0.01):
    order = Order(access_id, secret_key)

    market_depth = Data.get_market_depth(limit=1)
    bid_price, bid_amount = map(float, market_depth["data"]["bids"][0])
    ask_price, ask_amount = map(float, market_depth["data"]["asks"][0])

    if price > ask_price or price < bid_price:
        print "Shit, your deal is going to be eaten, change your price."
        return 0

    order.order_limit("buy", price=price, amount=amount)
    order.order_limit("sell", price=price, amount=amount)
    order.withdraw_all()


def top_price():
    market_depth = Data.get_market_depth(limit=1)
    bid_price, bid_amount = map(float, market_depth["data"]["bids"][0])
    ask_price, ask_amount = map(float, market_depth["data"]["asks"][0])
    return ask_price - 0.01


def butt_price():
    market_depth = Data.get_market_depth(limit=1)
    bid_price, bid_amount = map(float, market_depth["data"]["bids"][0])
    ask_price, ask_amount = map(float, market_depth["data"]["asks"][0])
    return bid_price + 0.01


order = Order(access_id, secret_key)
