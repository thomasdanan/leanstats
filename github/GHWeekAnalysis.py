#!/usr/bin/python
import getpass
from dateutil.parser import parse
from datetime import timedelta
import pytz


from ScalityIssue import ScalityIssue
from GHClient import GHClient
from GHUtils import GHUtils


class GHWeekAnalysis:

    ghClient = None

    def __init__(self, ghClient):
        self.ghClient = ghClient


    def getIssuesSummary(self, scalityIssues):
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
            if backlogItem.containsLabel('bug'):
                bugs += 1
                if GHUtils.isDateInRange(startDate, endDate, createdDate):
                    bugsInPeriod += 1
            elif backlogItem.containsLabel('debt'):
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
#start = '2019-07-08'
end = input("end (YYYY-MM-DD): ").strip()
#end = '2019-07-14'
#go there to generate one: https://github.com/settings/tokens
accessToken = input("personal access token: ").strip()

ghClient = GHClient(accessToken)
ghWeekAnalysis = GHWeekAnalysis(ghClient)

scalityIssues = []
issuesUrl = "https://api.github.com/search/issues?q=is:issue+is:closed+repo:scality/metalk8s+closed:"+start+".."+end+"&per_page=100"
issues = ghClient.collectItems(issuesUrl)
for issue in issues:
    scalityIssue = ScalityIssue.toScalityIssue(issue, ghClient)
    scalityIssues.append(scalityIssue)
issuesSummary = ghWeekAnalysis.getIssuesSummary(scalityIssues)

scalityPrs = []
prsUrl = "https://api.github.com/search/issues?q=is:pr+is:merged+repo:scality/metalk8s+merged:"+start+".."+end+"&per_page=100"
prs = ghClient.collectItems(prsUrl)
for pr in prs:
    scalityPr = ScalityIssue.toScalityIssue(pr, ghClient)
    scalityPrs.append(scalityPr)
prsSummary = ghWeekAnalysis.getPrsSummary(scalityPrs)


backlogItems = []
backlogUrl = "https://api.github.com/search/issues?q=is:issue+is:open+repo:scality/metalk8s&per_page=100"
issues = ghClient.collectItems(backlogUrl)
for issue in issues:
    backlogItem = ScalityIssue.toScalityIssue(issue, ghClient)
    backlogItems.append(backlogItem)
backlogSummary = ghWeekAnalysis.getBacklogSummary(backlogItems, start, end)

print ("copy in https://docs.google.com/spreadsheets/d/1ebrg_dyWGUKF_20LBlYMJvMX5pr2NMChB-j8HQPBvtc/edit#gid=1173901207")
print ("merged PRs,in std,out std, avg merge time,in std,no estimation,out std,avg elapsed days,bugsInPeriod,debtsInPeriod,othersInPeriod,bugs,debts,others")
print (prsSummary + "," + issuesSummary + "," + backlogSummary)
