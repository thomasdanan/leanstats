#!/usr/bin/python

import json
import sys
import datetime
import math
import requests
import getpass
import numpy as np

from GitHubClient import GitHubClient


from requests.auth import HTTPBasicAuth

import re

from dateutil.parser import parse

class GitHubPRs:

    githubClient = None

    def __init__(self, githubClient):
        self.githubClient = githubClient

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
            events = githubClient.collectItems(eventsUrl)
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
                    print (str(prTfm) + "," + self.getDayDate(created) + "," + self.getDayDate(closed) + "," + pr['user']['login'] + "," + pr['title'] + "," + pr['html_url'])
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

start = raw_input("start (YYYY-MM-DD): ")
#start = '2019-04-22'
end = raw_input("end (YYYY-MM-DD): ")
#end = '2019-04-28'
user = raw_input("github id: ")
#user = 'thomasdanan'
passwd = getpass.getpass()
githubClient = GitHubClient(user, passwd)
githubPrs = GitHubPRs(githubClient)
url = "https://api.github.com/search/issues?q=is:pr+is:merged+repo:scality/metalk8s+merged:"+start+".."+end+"&per_page=100"
prs = githubClient.collectItems(url)
githubPrs.parsePrs(prs)
