# -*- coding:utf-8 -*-
# 这是对viabtd.com的API进行的封装。
# author: LucasPHBS
# update: 20170811

##
from __future__ import unicode_literals
from ViabtcAPI import ViabtcData as Data
from ViabtcAPI import ViabtcOrder as Order
import numpy as np
import pandas as pd
import time
import talib


##
class DataStore(object):

    def __init__(self):
        self.data_types = ["1min", "3min", "15min", "30min", "1hour",
                             "2hour", "4hour", "6hour", "12hour", "1day", "3day", "1week"]
        self.markets = ["BTCCNY", "BCCCNY", "BCCBTC", "LTCCNY", "ETHCNY", "ZECCNY", "148ETH"]

    data_types = ["1min", "3min", "15min", "30min", "1hour",
                  "2hour", "4hour", "6hour", "12hour", "1day", "3day", "1week"]

    markets = ["BTCCNY", "BCCCNY", "BCCBTC", "LTCCNY", "ETHCNY", "ZECCNY", "148ETH"]

    # 1. 储存数据的单次方法
    @staticmethod
    def store_data(data_type, market="BCCCNY"):
        """

        :param data_type:

            1min : 1分钟；
            3min:3分钟；
            5min : 5分钟;
            15min:15分钟；
            30min:30分钟；
            1hour:1小时；
            2hour:2小时；
            4hour:4小时；
            6hour:6小时；
            12hour:12小时；
            1day:1日；
            3day:3日；
            1week:1周；

        :param market: one from market list
        :return:
        """
        target = "data/" + market + "_" + data_type + ".csv"

        # 得到最新的从老到新排列的数据
        candles = Data.get_candles(type=data_type, market=market).get("data")
        candles_df = pd.DataFrame(candles,
                                  columns=["time", "open", "close", "high", "low", "vol"])

        # 得到过去从老到新排列的数据
        try:
            # 如果老数据存在
            old_candles_df = pd.DataFrame.from_csv(target)
            merge_candles = pd.concat([old_candles_df, candles_df])
            csv = merge_candles.drop_duplicates("time", keep="first").reset_index(drop=True)
            print len(csv)
            csv.to_csv(target)
        except:
            # 如果老数据不存在
            print "1st time to store data, just create one."
            csv = candles_df
            print len(csv)
            csv.to_csv(target)

    # 2. 下载数据的持续化方法
    @staticmethod
    def collect_data(data_type, sleeptime, market="BCCCNY"):
        try:
            while 1:
                DataStore.store_data(data_type=data_type, market=market)
                time.sleep(sleeptime)
        except:  # 如果出问题后自动刷新
            print "something wrong, retry in 5 seconds"
            time.sleep(5)
            DataStore.collect_data(data_type=data_type, market=market)

    # 3. 将数据刷新一次
    @staticmethod
    def refresh_data_in(market="BCCCNY"):  # 出问题后已经会自动刷新了
        for i in DataStore.data_types:
            print "\n# refreshing " + i + " data in " + market + " market #"
            DataStore.store_data(data_type=i, market=market)
        print "\n# " + market + " data-refresing done."

    # 4. 将全部市场数据都刷新一次
    @staticmethod
    def refresh_data_in_all_markets():
        for market in DataStore.markets:
            DataStore.refresh_data_in(market=market)  # 出问题后已经会自动刷新了

##
#
# times = pd.DataFrame.from_csv("data/BTCCNY_30min.csv").time + 8 * 60 * 60
# times = pd.to_datetime(times, unit="s")
#
# ##
# bcccny1min = pd.DataFrame.from_csv("data/BTCCNY_30min.csv")
# bcccny1min.time += 8 * 60 * 60
# bcccny1min.time = pd.to_datetime(times, unit = "s")
#
# ##
# a = talib.MACD(bcccny1min.close.as_matrix())
# a = pd.DataFrame([pd.Series(a[i]) for i in range(3)]).T
# a.columns = ["sma9", "sma21", "macd-hist"]
# ##
# sma = pd.concat([bcccny1min, a], axis=1)
#
#
# ##
# sma9 = talib.SMA(bcccny1min.close.as_matrix(), 15)
# sma9 = pd.Series(sma9)
# sma9.name = "sma9"
# sma = pd.concat([bcccny1min, sma9], axis=1)
#
# sma21 = talib.SMA(bcccny1min.close.as_matrix(), 60)
# sma21 = pd.Series(sma21)
# sma21.name = "sma21"
# sma = pd.concat([sma, sma21], axis=1)
#
#
# ##
# def sma_roll():
#     roll = []
#     last_time = False
#     buy_times = 0
#     sell_times = 0
#     capital = {"CNY": 17500.0,
#                "BCC": 0.0,
#                "Value": 17500.0}
#
#     def buy(capital, price):
#         return {"CNY": 0,
#                 "BCC": capital["BCC"] + capital["CNY"]/float(price)*999/1000,
#                 "Value": capital["BCC"] + capital["CNY"]*999/1000}
#
#     def sell(capital, price):
#         return {"CNY": capital["CNY"] + capital["BCC"]*float(price)*999/1000,
#                 "BCC": 0,
#                 "Value": capital["CNY"] + capital["BCC"]*float(price)*999/1000}
#
#     def hold(capital, price):
#         return {"CNY": capital["CNY"],
#                 "BCC": capital["BCC"],
#                 "Value": capital["CNY"] + capital["BCC"]*float(price)}
#
#     def cpt(capital, price, act):
#         if act == "buy":
#             return buy(capital, price)
#         elif act == "sell":
#             return sell(capital, price)
#         else:
#             return hold(capital, price)
#
#     def action(this_time, last_time=last_time):
#         if (not last_time) and this_time == True:
#             return "buy"
#         elif (not this_time) and last_time:
#             return "sell"
#         elif last_time and this_time:
#             return "still_up"
#         else:
#             return "still_down"
#
#     for i in range(pd.DataFrame.__len__(sma)):
#         sma_now = sma.loc[i]
#         this_time = sma.loc[i]["sma9"] > sma.loc[i]["sma21"]
#         lst = last_time
#         act = action(this_time, lst)
#         cap = cpt(capital, sma_now["close"], act)
#
#         status = {"time": sma_now["time"],
#                   "close": sma_now["close"],
#                   "vol": sma_now["vol"],
#                   "sma9": sma_now["sma9"],
#                   "sma21": sma_now["sma21"],
#                   "this_time": this_time,
#                   "last_time": lst,
#                   "action": act,
#                   "capital": cap}
#
#         last_time = this_time
#         capital = cap
#         roll.append(status)
#
#     return roll
#
# sr = sma_roll()
# values = [i["capital"]["Value"] for i in sr]
# prices = [i["close"] for i in sr]
# srpd = pd.DataFrame([values, prices]).T
# srpd.columns = ["values", "prices"]
#
# ##
# srpd.plot()