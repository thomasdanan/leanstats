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

class GHIssuesKPI:

    ghClient = None

    def __init__(self, ghClient):
        self.ghClient = ghClient

    def printIssuesSummary(self, scalityIssues):
        # sort by issue start date
        nbrClosed = len(scalityIssues)
        nbrInStd = 0
        nbrNotEstimated = 0
        cummulatedTime = 0
        for scalityIssue in scalityIssues:
            cummulatedTime += scalityIssue.getElapsedHours()
            if scalityIssue.getComplexity() == "Unknown":
                nbrNotEstimated += 1
            elif scalityIssue.isInStd():
                nbrInStd += 1
        avgElapsedHours = cummulatedTime / nbrClosed
        elapsedDays = "%.1f" % (avgElapsedHours / 24.0)

        nbrOutStd = nbrClosed - nbrNotEstimated - nbrInStd
        print "in std;no estimation;out std;avg elapsed days"
        print str(nbrInStd)+";"+str(nbrNotEstimated)+";"+str(nbrOutStd)+";"+str(elapsedDays)

start = raw_input("start (YYYY-MM-DD): ")
#start = '2019-02-04'
end = raw_input("end (YYYY-MM-DD): ")
#end = '2019-02-10'
user = raw_input("github id: ")
#user = 'thomasdanan'
passwd = getpass.getpass()
ghClient = GHClient(user, passwd)
ghIssuesKPI = GHIssuesKPI(ghClient)
scalityIssues = []
url = "https://api.github.com/search/issues?q=is:issue+is:closed+repo:scality/metalk8s+closed:"+start+".."+end+"&per_page=100"
issues = ghClient.collectItems(url)
for issue in issues:
    scalityIssue = ScalityIssue.toScalityIssue(issue, ghClient)
    scalityIssues.append(scalityIssue)
ghIssuesKPI.printIssuesSummary(scalityIssues)
