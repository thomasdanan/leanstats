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
        nbrMergedPrs = 0
        cumulatedTfm = 0
        for pr in prs:
            #tfm = time for merge: time between ready for review and merge

            prid = pr['number']
            # for standard PRs, ready for review date is equivalent to PR open date
            created = parse(pr['created_at'])
            closed = parse(pr['closed_at'])
            eventsUrl = pr['events_url']
            events = self.collectItems(eventsUrl)
            ready_review = self.getEventDate(events,'ready_for_review')
            # for draft PRs, ready for review date is available in event list
            if ready_review is not None:
                created = ready_review
            #merged = self.getEventDate(events, 'merged')
            if created is not None and closed is not None:
                nbrMergedPrs = nbrMergedPrs + 1
                prTfm = self.getDeltaWEExcluded(created, closed)
                cumulatedTfm = cumulatedTfm + prTfm
                if prTfm > 36:
                    print ("time,"+ str(prTfm) + ",created," + self.getDayDate(created) + ",closed," + self.getDayDate(closed) + "," + pr['user']['login'] + "," + pr['title'] + "," + pr['html_url'])
        print( "nbr of merged PRs: " + str(nbrMergedPrs) )
        print ("avg tfm (hours) = " + str(cumulatedTfm / nbrMergedPrs))

    def getEventDate(self, events, eventKey):
        for event in events:
            if event['event'] == eventKey:
                return parse(event['created_at'])
        return None

    def getDayDate(self, date):
        return str(date.strftime("%Y-%m-%d"))


    def getDeltaWEExcluded(self, start, end):
        # don't count weekends
        deltadays = np.busday_count( self.getDayDate(start), self.getDayDate(end) )
        deltahours = end.hour - start.hour
        tfm = (deltadays * 24) + deltahours
        return tfm

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



start = raw_input("start (YYYY-MM-DD): ")
#start = '2019-04-12'
end = raw_input("end (YYYY-MM-DD): ")
#end = '2019-04-12'
#user = raw_input("github id: ")
#user = 'thomasdanan'
passwd = getpass.getpass()
githubstats = GitHubStats(user, passwd)
url = "https://api.github.com/search/issues?q=is:pr+is:merged+repo:scality/metalk8s+merged:"+start+".."+end+"&per_page=100"
prs = githubstats.collectItems(url)
githubstats.parsePrs(prs)
