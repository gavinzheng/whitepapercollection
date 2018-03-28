#!/usr/bin/python
# -*- coding: utf-8 -*-
#用于进行http请求，以及MD5加密，生成签名的工具类

import http.client
import urllib
import json
import hashlib
import time
import requests
from urllib.parse import urljoin
from urllib.parse import urlencode

def buildMySign(params,secretKey):
    sign = ''
    for key in sorted(params.keys()):
        sign += key + '=' + str(params[key]) +'&'
    data = sign+'secret_key='+secretKey
    return  hashlib.md5(data.encode("utf8")).hexdigest().upper()

def httpGet(url,resource,params=''):
    r = requests.get(url+ resource + '?' + params, timeout=10)
    try:
        return r.json()
    except ValueError as e:
        print(r.text)
        raise

def httpPost(url,resource,params):
    headers = {
        "Content-type" : "application/x-www-form-urlencoded",
    }

    url = urljoin(url, resource)
    params = urllib.parse.urlencode(params)
    r = requests.post(url, headers=headers, data=params, timeout=10)
    try:
        return r.json()
    except ValueError as e:
        print(r.text)
        raise
 
