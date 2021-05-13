#!/usr/bin/python

import json
import sys
import datetime
import math
import requests
import getpass
import numpy as np

from requests.auth import HTTPBasicAuth

import re

from dateutil.parser import parse

class GHClient:
    token = ''

    def __init__(self, token):
        self.token = token

    ## Link: <https://api.github.com/repositories/124905930/pulls?state=closed&page=17>; rel="prev", <https://api.github.com/repositories/124905930/pulls?state=closed&page=1>; rel="first"
    def getNextPageUrl(self, headers):
        if 'Link' in headers.keys():
            link = headers['Link']
            matchs = re.search("<(http[^<]*)>; rel=\"next\"", link)
            if matchs != None:
                return matchs.group(1)
        return None

    def collectItem(self, url, headers):
        if not headers:
            headers = {}
        item = None
        headers['Authorization'] = 'token %s' % self.token
        myResponse = requests.get(url, headers=headers)
        if(myResponse.ok):
            item = json.loads(myResponse.content)
        else:
            myResponse.raise_for_status()
        return item

    def collectItems(self, url, **headers):
        nextPageUrl = url
        items = []
        while nextPageUrl != None:
            if not headers:
                headers = {}
            headers['Authorization'] = 'token %s' % self.token
            myResponse = requests.get(nextPageUrl, headers=headers)
            if(myResponse.ok):
                nextPageUrl = self.getNextPageUrl(myResponse.headers)
                jsonResult = json.loads(myResponse.content)
                if type(jsonResult) == list:
                    items = items + jsonResult
                else:
                    items = items + jsonResult['items']
            else:
                myResponse.raise_for_status()
        return items
