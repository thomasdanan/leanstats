#!/usr/bin/python

import json
import sys
import datetime
import math
import getpass
from dateutil.parser import parse
from ScalityIssue import ScalityIssue
from GHClient import GHClient
from GHUtils import GHUtils

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
                scalityIssue = ScalityIssue.toScalityIssue(issue, self.ghClient)
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
            assignee = scalityIssue.getAssignee()
            start = scalityIssue.getStartDate()
            end = issue['closed_at']
            # if issue is opened, no end date so elapsed is time between start date and now
            if state == 'open':
                end = 'None'
            else:
                end = GHUtils.getDayDate(parse(end))

            elapsedHours = scalityIssue.getElapsedHours()
            elapsedDays = "%.1f" % (elapsedHours / 24.0)
            print str(number)+";"+issue['title']+";"+complexity+";"+assignee+";"+GHUtils.getDayDate(start)+";"+end+";"+elapsedDays

url = raw_input("url: ")
user = raw_input("github id: ")
#user = 'thomasdanan'
passwd = getpass.getpass()
ghClient = GHClient(user, passwd)
ghIssues = GHIssues(ghClient)
closedInProgress = []
#url = "https://api.github.com/search/issues?q=is:issue+repo:scality/metalk8s+milestone:\"MetalK8s 2.0.0-alpha4\"&per_page=100"
issues = ghClient.collectItems(url)
closedInProgress = closedInProgress + ghIssues.filterClosedInProgress(issues)
ghIssues.printIssuesSummary(closedInProgress)
