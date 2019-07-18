#!/usr/bin/python
from dateutil.parser import parse
import datetime
from GHUtils import GHUtils

# can be GH Issue or GH Pull request
class ScalityIssue:
    issue = None
    events = None
    ghClient = None
    def __init__(self, issue, ghClient):
        self.issue = issue
        self.ghClient = ghClient

    def getEvents(self):
        if self.events == None:
            self.events = self.ghClient.collectItems(self.issue['events_url'])
        return self.events

    def getComplexity(self):
        if self.containsLabel('easy'):
            return 'easy'
        elif self.containsLabel('medium'):
            return 'medium'
        elif self.containsLabel('hard'):
            return 'hard'
        else:
            return "Unknown"

    def changeCreated(self, created):
        self.issue['created'] = created

    def getIssue(self):
        return self.issue

    def containsLabel(self, searchLabel):
        labels = self.issue['labels']
        for label in labels:
            if label['name'] == searchLabel:
                return True
        return False

    def isBlocked(self):
        return self.containsLabel('blocked')

    def getAssignee(self):
        if self.issue['assignee'] != None:
            return self.issue['assignee']['login']
        elif 'pull_request' in self.issue.keys():
            return self.issue['user']['login']
        else: return "Unknown"

    def getEndDate(self):
        state = self.issue['state']
        end = self.issue['closed_at']
        # if issue is opened, no end date so elapsed is time between start date and now
        if state == 'open':
            return datetime.datetime.now()
        else:
            return parse(end)

    def getStartDate(self):
        # for draft PRs, ready for review date is available in event list
        if 'pull_request' in self.issue.keys() and GHUtils.getFirstEventDate(self.getEvents(),'ready_for_review') != None:
            return GHUtils.getFirstEventDate(self.getEvents(),'ready_for_review')
        # for issues, count from last assignee event (does not apply for PRs)
        elif 'pull_request' not in self.issue.keys() and self.issue['assignee'] != None:
            return GHUtils.getLastEventDate(self.getEvents(),'assigned')
        # in all other cases, use created_at
        else:
            return parse(self.issue['created_at'])

    def getCreatedAt(self):
        return parse(self.issue['created_at'])

    def getAge(self):
        return GHUtils.getFirstEventDate(self.getEvents(),'assigned')

    def getElapsedHours(self):
        start = self.getStartDate()
        end = self.getEndDate()
        return GHUtils.getDeltaWEExcluded(start, end)

    def getElapsedDays(self):
        elapsedHours = self.getElapsedHours()
        elapsedDays = "%.1f" % (elapsedHours / 24.0)
        return elapsedDays

    def isInStd(self):
        elapsedHours = self.getElapsedHours()
        complexity = self.getComplexity()
        if complexity == "easy" and elapsedHours <= 24:
            return True
        elif complexity == "medium" and elapsedHours <= 72:
            return True
        elif complexity == "hard" and elapsedHours <= 120:
            return True
        else:
            return False

    @staticmethod
    def toScalityIssue(issue, ghClient):
        scalityIssue = ScalityIssue(issue, ghClient)
        return scalityIssue
