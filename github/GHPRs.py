#!/usr/bin/python

import json
import sys
import datetime
import math
import getpass
from dateutil.parser import parse

from GHClient import GHClient
from GHUtils import GHUtils


class GHPRs:

    githubClient = None

    def __init__(self, ghClient):
        self.ghClient = ghClient

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
            events = ghClient.collectItems(eventsUrl)
            ready_review = GHUtils.getFirstEventDate(events,'ready_for_review')
            # for draft PRs, ready for review date is available in event list
            if ready_review is not None:
                created = ready_review
            if created is not None and closed is not None:
                nbrMergedPrs = nbrMergedPrs + 1
                prTfm = GHUtils.getDeltaWEExcluded(created, closed)
                cumulatedTfm = cumulatedTfm + prTfm
                if prTfm > 36:
                    print (str(prTfm) + "," + GHUtils.getDayDate(created) + "," + GHUtils.getDayDate(closed) + "," + pr['user']['login'] + "," + pr['title'] + "," + pr['html_url'])
        print( "nbr of merged PRs: " + str(nbrMergedPrs) )
        print ("avg tfm (hours) = " + str(cumulatedTfm / nbrMergedPrs))


start = raw_input("start (YYYY-MM-DD): ")
#start = '2019-04-22'
end = raw_input("end (YYYY-MM-DD): ")
#end = '2019-04-25'
user = raw_input("github id: ")
#user = 'thomasdanan'
passwd = getpass.getpass()
ghClient = GHClient(user, passwd)
ghPRs = GHPRs(ghClient)
url = "https://api.github.com/search/issues?q=is:pr+is:merged+repo:scality/metalk8s+merged:"+start+".."+end+"&per_page=100"
prs = ghClient.collectItems(url)
ghPRs.parsePrs(prs)
