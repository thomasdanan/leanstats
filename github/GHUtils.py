
#!/usr/bin/python

import json
import sys
import datetime
import math
import getpass
import numpy as np
from dateutil.parser import parse


class GHUtils:

    @staticmethod
    def getLastEventDate(events, eventKey):
        for event in reversed(events):
            if event['event'] == eventKey:
                return parse(event['created_at'])
        return None

    @staticmethod
    def getFirstEventDate(events, eventKey):
        for event in events:
            if event['event'] == eventKey:
                return parse(event['created_at'])
        return None

    @staticmethod
    def getWeekNumber(date):
        return str(date.isocalendar()[0])+"-"+str(date.isocalendar()[1]).zfill(2)

    @staticmethod
    def getDayDate(date):
        return str(date.strftime("%Y-%m-%d"))

    @staticmethod
    def getDeltaWEExcluded(start, end):
        # don't count weekends
        deltadays = np.busday_count( GHUtils.getDayDate(start), GHUtils.getDayDate(end) )
        deltahours = end.hour - start.hour
        tfm = (deltadays * 24) + deltahours
        return tfm

    @staticmethod
    def isDateInRange(start, end, date):
        return date >= start and date < end
