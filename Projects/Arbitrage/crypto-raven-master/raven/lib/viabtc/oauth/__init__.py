#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created by bu on 2017-05-10
"""
import json as complex_json
import requests
from .utils import verify_sign
from .utils import get_sign


class RequestClient(object):
    __headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
    }

    def __init__(self, access_id, secret_key, headers=dict()):
        self.access_id = access_id
        self.secret_key = secret_key
        self.headers = self.__headers
        self.headers.update(headers)

    def set_authorization(self, params):
        params['access_id'] = self.access_id
        self.headers['access_id'] = self.access_id
        self.headers['AUTHORIZATION'] = get_sign(params, self.secret_key)

    def request(self, method, url, params=dict(), data='', json=dict()):
        method = method.upper()
        if method == 'GET':
            self.set_authorization(params)
            result = requests.request('GET', url, params=params, headers=self.headers)
        else:
            if data:
                json.update(complex_json.loads(data))
            self.set_authorization(json)
            result = requests.request(method, url, json=json, headers=self.headers)
        return result


class OAuthClient(object):
    def __init__(self, request):
        self.request = request
        self._body = dict()
        self._authorization = ''

    @property
    def body(self):
        raise NotImplementedError('extract body')

    @property
    def authorization(self):
        raise NotImplementedError('authorization')

    def verify_request(self, secret_key):
        return verify_sign(self.body, secret_key, self.authorization)


class FlaskOAuthClient(OAuthClient):
    @property
    def body(self):
        if self._body:
            return self._body

        if self.request.method == 'GET':
            self._body = self.request.args.to_dict()
        elif self.request.is_json:
            self._body = self.request.json

        access_id = self.request.headers.get('ACCESS_ID')
        if access_id:
            self._body['access_id'] = access_id
        return self._body

    @property
    def authorization(self):
        if self._authorization:
            return self._authorization

        self._authorization = self.request.headers['AUTHORIZATION']
        return self.authorization

