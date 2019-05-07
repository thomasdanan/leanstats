#!/usr/bin/python

import json
import sys
import datetime
import math
import getpass
from dateutil.parser import parse

from GHClient import GHClient
from GHUtils import GHUtils

class GHIssues:

    ghClient = None

    def __init__(self, ghClient):
        self.ghClient = ghClient

    def parseIssues(self, prs, complexity):
        print "number;complexity;assignee;start;end;elapsed"
        for issue in issues:
            #tfm = time for merge: time between ready for review and merge
            number = issue['number']
            state = issue['state']
            assignee = issue['assignee']
            if state == 'open' and assignee == None:
                continue
            eventsUrl = issue['events_url']
            events = ghClient.collectItems(eventsUrl)
            start = GHUtils.getEventDate(events,'assigned')
            end = issue['closed_at']
            if state == 'open':
                elapsedHours = GHUtils.getDeltaWEExcluded(start,datetime.datetime.now())
                end = 'None'
            else:
                elapsedHours = GHUtils.getDeltaWEExcluded(start,parse(end))
                end = GHUtils.getDayDate(parse(end))

            elapsedDays = "%.1f" % (elapsedHours / 24.0)

            print str(number)+";"+complexity+";"+str(assignee['login'])+";"+GHUtils.getDayDate(start)+";"+end+";"+elapsedDays

user = raw_input("github id: ")
#user = 'thomasdanan'
passwd = getpass.getpass()
ghClient = GHClient(user, passwd)
ghIssues = GHIssues(ghClient)
complexities = {'easy', 'medium', 'hard'}
for complexity in complexities:
    url = "https://api.github.com/search/issues?q=is:issue+repo:scality/metalk8s+milestone:\"MetalK8s 2.0.0-alpha4\"+label:"+complexity+"&per_page=100"
    issues = ghClient.collectItems(url)
    ghIssues.parseIssues(issues, complexity)
