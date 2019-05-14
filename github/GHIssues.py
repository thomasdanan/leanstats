#!/usr/bin/python

import json
import sys
import datetime
import math
import getpass
from dateutil.parser import parse

from GHClient import GHClient
from GHUtils import GHUtils


class ScalityIssue:
    issue = None
    complexity = None
    events = None
    def __init__(self, issue, complexity, events):
        self.issue = issue
        self.complexity = complexity
        self.events = events

    def getComplexity(self):
        return self.complexity

    def getIssue(self):
        return self.issue

    def getStartDate(self):
        return GHUtils.getLastEventDate(self.events,'assigned')

class GHIssues:

    ghClient = None

    def __init__(self, ghClient):
        self.ghClient = ghClient

    def filterClosedInProgress(self, issues):
        closedInProgress = []
        for issue in issues:
            #tfm = time for merge: time between ready for review and merge
            number = issue['number']
            state = issue['state']
            assignee = issue['assignee']
            # only consider closed and in progress (i.e. assignee not None)
            if state == 'open' and assignee == None:
                continue
            else:
                eventsUrl = issue['events_url']
                events = ghClient.collectItems(eventsUrl)
                scalityIssue = ScalityIssue(issue, complexity, events)
                closedInProgress.append(scalityIssue)
        return closedInProgress

    def printIssuesSummary(self, scalityIssues):
        # sort by issue start date
        scalityIssues.sort(key=ScalityIssue.getStartDate)
        for scalityIssue in scalityIssues:
            issue = scalityIssue.getIssue()
            complexity = scalityIssue.getComplexity()
            number = issue['number']
            state = issue['state']
            assignee = issue['assignee']
            start = scalityIssue.getStartDate()
            end = issue['closed_at']
            # if issue is opened, no end date so elapsed is time between start date and now
            if state == 'open':
                elapsedHours = GHUtils.getDeltaWEExcluded(start,datetime.datetime.now())
                end = 'None'
            else:
                elapsedHours = GHUtils.getDeltaWEExcluded(start,parse(end))
                end = GHUtils.getDayDate(parse(end))

            elapsedDays = "%.1f" % (elapsedHours / 24.0)
            print str(number)+";"+issue['title']+";"+complexity+";"+str(assignee['login'])+";"+GHUtils.getDayDate(start)+";"+end+";"+elapsedDays

user = raw_input("github id: ")
#user = 'thomasdanan'
passwd = getpass.getpass()
ghClient = GHClient(user, passwd)
ghIssues = GHIssues(ghClient)
closedInProgress = []
complexities = {'easy', 'medium', 'hard'}
for complexity in complexities:
    url = "https://api.github.com/search/issues?q=is:issue+repo:scality/metalk8s+milestone:\"MetalK8s 2.0.0-alpha4\"+label:"+complexity+"&per_page=100"
    issues = ghClient.collectItems(url)
    closedInProgress = closedInProgress + ghIssues.filterClosedInProgress(issues)
ghIssues.printIssuesSummary(closedInProgress)
