#!/usr/bin/python
import getpass
from dateutil.parser import parse
from datetime import timedelta
import pytz
import json


from ScalityIssue import ScalityIssue
from ScalityProject import ScalityProject

from GHClient import GHClient
from GHUtils import GHUtils


class GHWeekAnalysis:

    repo=None
    ghClient = None

    def __init__(self, repos, ghClient):
        self.repos = repos
        self.ghClient = ghClient

    def getIssuesSummary(self, scalityIssues):
        # sort by issue start date
        nbrClosed = len(scalityIssues)
        nbrInStd = 0
        nbrNotEstimated = 0
        cummulatedTime = 0
        elapsedDays = 0
        nbrOutStd = 0
        if nbrClosed > 0:
          for scalityIssue in scalityIssues:
              cummulatedTime += scalityIssue.getElapsedHours()
              if scalityIssue.getComplexity() == "Unknown":
                  nbrNotEstimated += 1
              elif scalityIssue.isInStd():
                  nbrInStd += 1
          avgElapsedHours = cummulatedTime / nbrClosed
          elapsedDays = "%.1f" % (avgElapsedHours / 24.0)
          nbrOutStd = nbrClosed - nbrNotEstimated - nbrInStd
        print ("##### Issues Summary #####")
        print ("in std: " + str(nbrInStd))
        print ("no estimation: " + str(nbrNotEstimated))
        print ("out std: " + str(nbrOutStd))
        print ("avg elapsed days: " + str(elapsedDays))
        return (str(nbrInStd)+","+str(nbrNotEstimated)+","+str(nbrOutStd)+","+str(elapsedDays))

    def printSuspiciousPR(self, scalityPrs):
        print ("suspicious Prs")
        for scalityPr in scalityPrs:
            pr = scalityPr.getIssue()
            prid = pr['number']
            created = scalityPr.getStartDate()
            closed = scalityPr.getEndDate()
            tfm = scalityPr.getElapsedHours()
            print (str(tfm) + "," + GHUtils.getDayDate(created) + "," + GHUtils.getDayDate(closed) + "," + pr['user']['login'] + "," + pr['title'] + "," + pr['html_url'])

    def getPrsSummary(self, scalityPrs):
        nbrMerged = len(scalityPrs)
        nbrInStd = nbrMerged
        cummulatedTime = 0
        suspiciousPrs = []
        for scalityPr in scalityPrs:
            tfm = scalityPr.getElapsedHours()
            cummulatedTime += tfm
            if tfm > 36:
                nbrInStd -= 1
                suspiciousPrs.append(scalityPr)
        print ("##### PRs Summary #####")
        print ("merged PRs: " + str(nbrMerged))
        print ("in std: " + str(nbrInStd))
        print ("out std: " + str(nbrMerged - nbrInStd))
        print ("avg merge time: " + str(cummulatedTime / nbrMerged))
        self.printSuspiciousPR(suspiciousPrs)
        return  str(nbrMerged) + "," + str(nbrInStd) + "," + str(nbrMerged - nbrInStd) + "," + str(cummulatedTime / nbrMerged)

    def getBacklogSummary(self, backlogItems, start, end):
        paris = pytz.timezone('Europe/Paris')
        startDate = parse(start)
        startDate = paris.localize(startDate)

        endDate = parse(end) + timedelta(days=1)
        endDate = paris.localize(endDate)

        debts = 0
        bugs = 0
        others = 0
        debtsInPeriod = 0
        bugsInPeriod = 0
        othersInPeriod = 0
        issuesUrl = "https://api.github.com/search/issues?q=is:issue+is:open+repo:scality/metalk8s&per_page=100"
        issues = ghClient.collectItems(issuesUrl)
        for backlogItem in backlogItems:
            createdDate = backlogItem.getCreatedAt()
            if backlogItem.containsLabel('kind:bug'):
                bugs += 1
                if GHUtils.isDateInRange(startDate, endDate, createdDate):
                    bugsInPeriod += 1
            elif backlogItem.containsLabel('kind:debt'):
                debts += 1
                if GHUtils.isDateInRange(startDate, endDate, createdDate):
                    debtsInPeriod += 1
            else:
                others += 1
                if GHUtils.isDateInRange(startDate, endDate, createdDate):
                    othersInPeriod += 1
        print ("##### Backlog Summary #####")
        print ("bugsInPeriod: " + str(bugsInPeriod))
        print ("debtsInPeriod: " + str(debtsInPeriod))
        print ("othersInPeriod: " + str(othersInPeriod))
        print ("bugs: " + str(bugs))
        print ("debts: " + str(debts))
        print ("others: " + str(others))
        return  str(bugsInPeriod) + "," + str(debtsInPeriod) + "," + str(othersInPeriod) + "," + str(bugs) + "," + str(debts) + "," + str(others)


start = input("start (YYYY-MM-DD): ").strip()
end = input("end (YYYY-MM-DD): ").strip()
#go there to generate one: https://github.com/settings/tokens
accessToken = input("personal access token: ").strip()
#reposghargs="repo:scality/ringx+repo:scality/metalk8s+repo:scality/core-ui"
repos = input("'+' separated repo list ex: repo:scality/cloudserver+repo:scality/metalk8s: ").strip()

ghClient = GHClient(accessToken)
ghWeekAnalysis = GHWeekAnalysis(repos, ghClient)

scalityPrs = []
prsUrl = "https://api.github.com/search/issues?q=is:pr+is:merged+"+ghWeekAnalysis.repos+"+merged:"+start+".."+end+"&per_page=100"
prs = ghClient.collectItems(prsUrl)
for pr in prs:
    scalityPr = ScalityIssue.toScalityIssue(pr, ghClient)
    scalityPrs.append(scalityPr)
prsSummary = ghWeekAnalysis.getPrsSummary(scalityPrs)

print ("copy in https://docs.google.com/spreadsheets/d/1ebrg_dyWGUKF_20LBlYMJvMX5pr2NMChB-j8HQPBvtc/edit#gid=1173901207")
print ("merged PRs,in std,out std, avg merge time")
print (prsSummary)
