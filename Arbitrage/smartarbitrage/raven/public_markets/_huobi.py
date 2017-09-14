# Copyright (C) 2016, Philsong <songbohr@gmail.com>

import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market

HOST = "https://api.huobi.com/"
API_V3_URI = HOST + "apiv3/"

KlineUrl = HOST + "%s" + "/" + "%s" + "_kline_" + "%03d" + "_json.js"
QuotationUrl = HOST + "%s" + "/" + "ticker_%s_json.js"
DepthUrl = HOST + "%s/depth_%s_%d.js"
RealTimeTransactionUrl = HOST + "%s/detail_%s_json.js"

class Huobi(Market):
    accessKey = ""
    secretKey = ""
    market =""
    userAgent = ""

    def __init__(self, base_currency, market_currency, pair_code):
        super().__init__(base_currency, market_currency, pair_code)


        self.event = 'huobi_depth'
        self.subscribe_depth()

    def update_depth(self):
        url = 'http://api.huobi.com/staticmarket/depth_%s_50.js' % self.pair_code
        req = urllib.request.Request(url, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        res = urllib.request.urlopen(req)
        depth = json.loads(res.read().decode('utf8'))
        self.depth = self.format_depth(depth)


    def SendRequest(self, url, parameter) :
        # body: = ioutil.NopCloser(strings.NewReader(parameter)) // 把form数据编码
        # req, _:= http.NewRequest("POST", uri, body)
        # req.Header.Set("Content-Type", "application/x-www-form-urlencoded; param=value") // post方式需要
        # req.Header.Add("User-Agent", hb.userAgent)
        # resp, err:= hb.httpClient.Do(req) // 发送请求
        # data:= []byte{}
        # if err != nil
        # {
        #     return data, err
        # }
        # defer
        # resp.Body.Close() // 一定要关闭resp.Body
        # return ioutil.ReadAll(resp.Body)
        req = urllib.request.Request(url, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        res = urllib.request.urlopen(req)


    def SendTradingRequest(self, parameter):
        # if len(hb.accessKey) < 20 | | len(hb.secretKey) < 20
        # {
        #     return []
        #         byte{}, errors.New("error！the huobi AccessKey and SecretKey is incorrect.")
        # }

        url= API_V3_URI
        return SendRequest(self, url, parameter)


