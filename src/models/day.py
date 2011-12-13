'''
Created on Oct 12, 2011

@author: averaart
'''

from datetime import timedelta
from google.appengine.ext import db
from event import Event

class Day(db.Model):
    '''
    Every Event is divided into Days 
    '''
    date = db.DateTimeProperty()
    talks = db.IntegerProperty()
    event = db.ReferenceProperty(Event, collection_name="days")
    
    def end_time(self):
        return self.date + timedelta(minutes = self.talks * self.event.talk_time)
    
