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

class GitHubStats:
    user = ''
    password = ''

    def __init__(self, user, password):
        self.user = user
        self.password = password

    def load(self, file):
        with open(file) as jsonPRs:
            prs = json.load(jsonPRs)
            self.parsePrs(prs)


    def parsePrs(self, prs):
        nbrPrs = len(prs)
        print( "nbr of merged PRs: " + str(nbrPrs) )
        tfm = 0
        for pr in prs:
            prid = pr['number']
            closed = pr['closed_at']
            if closed is not None:
                tfm = tfm + self.getTimeForMerge(pr)
                if tfm > 36:
                    print ("suspicious PR ("+ str(tfm) +"): " + pr['html_url'])
        print ("avg tfm (hours) = " + str(tfm / nbrPrs))

    def getTimeForMerge(self, pr):
        created = parse(pr['created_at'])
        closed = parse(pr['closed_at'])
        # don't count weekends
        deltadays = np.busday_count( str(created.strftime("%Y-%m-%d")), str(closed.strftime("%Y-%m-%d")) )
        deltahours = closed.hour - created.hour

        tfm = deltadays * 24 + deltahours
        return tfm

      ## Link: <https://api.github.com/repositories/124905930/pulls?state=closed&page=17>; rel="prev", <https://api.github.com/repositories/124905930/pulls?state=closed&page=1>; rel="first"
    def getNextPage(self, headers):
        if 'Link' in headers.keys():
            link = headers['Link']
            matchs = re.search(".*page=([0-9]+)\>; rel=\"next\"", link)
            if matchs != None:
                return matchs.group(1)
        return None


    def collectPrs(self, url):
        nextPage = 1
        prs = []
        while nextPage != None:
            urlForPage = url + "&page=" + str(nextPage)
            #print urlForPage
            myResponse = requests.get(urlForPage, auth=HTTPBasicAuth(self.user, self.password))
            if(myResponse.ok):
                nextPage = self.getNextPage(myResponse.headers)
                prs = prs + json.loads(myResponse.content)['items']
            else:
                myResponse.raise_for_status()
        return prs



start = raw_input("start (YYYY-MM-DD): ")
end = raw_input("end (YYYY-MM-DD): ")
user = raw_input("github id: ")
passwd = getpass.getpass()
githubstats = GitHubStats(user, passwd)
url = "https://api.github.com/search/issues?q=is:pr+is:merged+repo:scality/metalk8s+merged:"+start+".."+end
prs = githubstats.collectPrs(url)
githubstats.parsePrs(prs)
