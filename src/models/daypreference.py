'''
Created on Oct 12, 2011

@author: averaart
'''

from google.appengine.ext import db
from day import Day
from guardian import Guardian

class DayPreference(db.Model):
    '''
    For each event a guardian can rank each available day.
    Each ranking is stored in a separate DayPreference.
    '''
    guardian_id = db.ReferenceProperty(Guardian, collection_name="day_preferences")
    day = db.ReferenceProperty(Day, collection_name="preferences")
    rank = db.IntegerProperty()

