'''
Created on Oct 12, 2011

@author: averaart
'''

from google.appengine.ext import db
from models.guardian import Guardian
from models.event import Event

class TimePreference(db.Model):
    '''
    For each event a guardian can indicate a preference for early or late in the evening.
    No preference is indicated with 0 (zero). Higher numbers indicate a preference for later in the evening.
    '''
    guardian_id = db.ReferenceProperty(Guardian, collection_name="time_preferences")
    event_id = db.ReferenceProperty(Event, collection_name="time_preferences")
    time_pref = db.IntegerProperty()

