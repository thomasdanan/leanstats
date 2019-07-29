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

class GHWIPIssues:

    ghClient = None

    def __init__(self, ghClient):
        self.ghClient = ghClient

    def printIssuesSummary(self, scalityIssues):
        # sort by issue start date
        scalityIssues.sort(key=ScalityIssue.getStartDate)
        for scalityIssue in scalityIssues:
            issue = scalityIssue.getIssue()
            complexity = scalityIssue.getComplexity()
            number = issue['number']
            state = issue['state']
            assignees = scalityIssue.getAssignees()
            start = scalityIssue.getStartDate()
            elapsedHours = scalityIssue.getElapsedHours()
            elapsedDays = "%.1f" % (elapsedHours / 24.0)
            print str(number)+","+issue['title']+","+complexity+","+assignees+","+GHUtils.getDayDate(start)+","+elapsedDays
            #print "=HYPERLINK(\"https://github.com/scality/metalk8s/issues/"+str(number)+"\",\""+str(number)+"\"),"+issue['title']+","+complexity+","+assignee+","+GHUtils.getDayDate(start)+","+elapsedDays

user = raw_input("github id: ")
#user = 'thomasdanan'
passwd = getpass.getpass()
ghClient = GHClient(user, passwd)
ghIssues = GHWIPIssues(ghClient)
scalityIssues = []
url = "https://api.github.com/search/issues?q=is:issue+is:open+repo:scality/metalk8s&per_page=100"
issues = ghClient.collectItems(url)
for issue in issues:
    if issue['assignee'] != None:
        scalityIssue = ScalityIssue.toScalityIssue(issue, ghClient)
        if not scalityIssue.isBlocked():
            scalityIssues.append(scalityIssue)
ghIssues.printIssuesSummary(scalityIssues)
