from lib.emailer import send_email
import datetime
import time
import config
import traceback
import os

class Snapshot(object):
    """docstring for ClassName"""
    def __init__(self):
        super(Snapshot, self).__init__()

    def _snapshot(self, filename, header, body):
        need_header = False

        if not os.path.exists(filename):
            need_header = True

        fp = open(filename, 'a+')

        if need_header:
            fp.write(header)

        fp.write(body)
        fp.close()

    def snapshot_balance(self, market, total_btc, total_bch):
        filename = 'snapshot_%s_balance.csv' % market
        header = "localtime, timestamp, total_btc, total_bch\n"

        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
        timestamp = time.time()
        body =("%s") % localtime +',' + ("%d") % timestamp +','+("%.4f") % total_btc+','+("%.2f") % total_bch +'\n'

        self._snapshot(filename, header, body)

        if market == "ALL":
            body =("localtime=%s, total_btc=%0.4f, total_bch=%0.4f") % (localtime, total_btc, total_bch)
            send_email('raven balance snapshot', body)
