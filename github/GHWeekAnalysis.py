#!/usr/bin/python
import getpass
from dateutil.parser import parse

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
        print "Issues Summary"
        print "in std: " + str(nbrInStd)
        print "no estimation: " + str(nbrNotEstimated)
        print "out std: " + str(nbrOutStd)
        print "avg elapsed days: " + str(elapsedDays)
        return str(nbrInStd)+","+str(nbrNotEstimated)+","+str(nbrOutStd)+","+str(elapsedDays)

    def printSuspiciousPR(self, scalityPrs):
        print "suspicious Prs"
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
        print "PRs Summary"
        print "merged PRs: " + str(nbrMerged)
        print "in std: " + str(nbrInStd)
        print "out std: " + str(nbrMerged - nbrInStd)
        print "avg merge time: " + str(cummulatedTime / nbrMerged)
        self.printSuspiciousPR(suspiciousPrs)
        return  str(nbrMerged) + "," + str(nbrInStd) + "," + str(nbrMerged - nbrInStd) + "," + str(cummulatedTime / nbrMerged)

#start = raw_input("start (YYYY-MM-DD): ")
start = '2019-07-08'
#end = raw_input("end (YYYY-MM-DD): ")
end = '2019-07-14'
user = raw_input("github id: ")
#user = 'thomasdanan'
passwd = getpass.getpass()
ghClient = GHClient(user, passwd)
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

print "copy in https://docs.google.com/spreadsheets/d/1ebrg_dyWGUKF_20LBlYMJvMX5pr2NMChB-j8HQPBvtc/edit#gid=1173901207"
print "merged PRs,in std,out std, avg merge time,in std,no estimation,out std,avg elapsed days"
print prsSummary + "," + issuesSummary
