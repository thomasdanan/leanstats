
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
    def getEventDate(events, eventKey):
        for event in events:
            if event['event'] == eventKey:
                return parse(event['created_at'])
        return None

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
