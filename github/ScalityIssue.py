#!/usr/bin/python
from dateutil.parser import parse
import datetime
from GHUtils import GHUtils

class ScalityIssue:
    issue = None
    complexity = None
    events = None
    def __init__(self, issue, complexity, events):
        self.issue = issue
        self.events = events
        self.complexity = complexity

    def getComplexity(self):
        return self.complexity

    def getIssue(self):
        return self.issue

    def getAssignee(self):
        if self.issue['assignee'] != None:
            return self.issue['assignee']['login']
        else: return "Unknown"

    def getStartDate(self):
        if self.issue['assignee'] != None:
            return GHUtils.getLastEventDate(self.events,'assigned')
        else:
            return parse(self.issue['created_at'])

    def getAge(self):
        return GHUtils.getFirstEventDate(self.events,'assigned')

    def getElapsedHours(self):
        state = self.issue['state']
        start = self.getStartDate()
        end = self.issue['closed_at']
        # if issue is opened, no end date so elapsed is time between start date and now
        if state == 'open':
            elapsedHours = GHUtils.getDeltaWEExcluded(start,datetime.datetime.now())
        else:
            elapsedHours = GHUtils.getDeltaWEExcluded(start,parse(end))
        return elapsedHours

    def getElapsedDays(self):
        elapsedHours = self.getElapsedHours()
        elapsedDays = "%.1f" % (elapsedHours / 24.0)
        return elapsedDays

    def isInStd(self):
        elapsedHours = self.getElapsedHours()
        if self.complexity == "easy" and elapsedHours <= 24:
            return True
        elif self.complexity == "medium" and elapsedHours <= 72:
            return True
        elif self.complexity == "hard" and elapsedHours <= 120:
            return True
        else:
            return False

    @staticmethod
    def toScalityIssue(issue, ghClient):
        eventsUrl = issue['events_url']
        events = ghClient.collectItems(eventsUrl)
        complexity = "Unknown"
        labels = issue['labels']
        for label in labels:
            if label['name']=='easy':
                complexity = "easy"
                break
            elif label['name']=='medium':
                complexity = "medium"
                break
            elif label['name']=='hard':
                complexity=  "hard"
                break
        scalityIssue = ScalityIssue(issue, complexity, events)
        return scalityIssue
