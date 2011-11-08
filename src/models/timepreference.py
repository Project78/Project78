'''
Created on Oct 12, 2011

@author: averaart
'''

from google.appengine.ext import db
from guardian import Guardian
from event import Event

class TimePreference(db.Model):
    '''
    For each event a guardian can indicate a preference for early or late in the evening.
    No preference is indicated with 0 (zero). Higher numbers indicate a preference for later in the evening.
    '''
    guardian = db.ReferenceProperty(Guardian, collection_name="time_preferences")
    event = db.ReferenceProperty(Event, collection_name="time_preferences")
    preference = db.IntegerProperty()

