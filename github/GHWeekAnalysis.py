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


    def getPrsSummary(self, prs):
        nbrMergedPrs = 0
        nbrMergedPrsOutOfStandard = 0
        cumulatedTfm = 0
        print "PRs Summary"
        print("suspicious Prs")
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
                nbrMergedPrs += 1
                prTfm = GHUtils.getDeltaWEExcluded(created, closed)
                cumulatedTfm = cumulatedTfm + prTfm
                if prTfm > 36:
                    nbrMergedPrsOutOfStandard += 1
                    print (str(prTfm) + "," + GHUtils.getDayDate(created) + "," + GHUtils.getDayDate(closed) + "," + pr['user']['login'] + "," + pr['title'] + "," + pr['html_url'])
        print "merged PRs: " + str(nbrMergedPrs)
        print "in std: " + str(nbrMergedPrs - nbrMergedPrsOutOfStandard)
        print "out std: " + str(nbrMergedPrsOutOfStandard)
        print "avg merge time: " + str(cumulatedTfm / nbrMergedPrs)
        return  str(nbrMergedPrs) + "," + str(nbrMergedPrs - nbrMergedPrsOutOfStandard) + "," + str(nbrMergedPrsOutOfStandard) + "," + str(cumulatedTfm / nbrMergedPrs)

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

prsUrl = "https://api.github.com/search/issues?q=is:pr+is:merged+repo:scality/metalk8s+merged:"+start+".."+end+"&per_page=100"
prs = ghClient.collectItems(prsUrl)
prsSummary = ghWeekAnalysis.getPrsSummary(prs)

print "merged PRs,in std,out std, avg merge time,in std,no estimation,out std,avg elapsed days"
print prsSummary + "," + issuesSummary
