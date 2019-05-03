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

class GitHubClient:
    user = ''
    password = ''

    def __init__(self, user, password):
        self.user = user
        self.password = password

    ## Link: <https://api.github.com/repositories/124905930/pulls?state=closed&page=17>; rel="prev", <https://api.github.com/repositories/124905930/pulls?state=closed&page=1>; rel="first"
    def getNextPageUrl(self, headers):
        if 'Link' in headers.keys():
            link = headers['Link']
            matchs = re.search("<(http[^<]*)>; rel=\"next\"", link)
            if matchs != None:
                return matchs.group(1)
        return None

    def collectItems(self, url):
        nextPageUrl = url
        items = []
        while nextPageUrl != None:
            myResponse = requests.get(nextPageUrl, auth=HTTPBasicAuth(self.user, self.password))
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
