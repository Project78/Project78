'''
Created on Oct 12, 2011

@author: averaart
'''

from datetime import timedelta
from google.appengine.ext import db
from event import Event
from datetime import timedelta

class Day(db.Model):
    '''
    Every Event is divided into Days 
    '''
    date = db.DateTimeProperty()
    talks = db.IntegerProperty()
    event = db.ReferenceProperty(Event, collection_name="days")
    end_time = db.DateTimeProperty()
    
    def updateEndTime(self):
        m = self.event.talk_time * self.talks
        d = timedelta(minutes=m)
        self.end_time = self.date + d
    
    def end_time(self):
        return self.date + timedelta(minutes = self.talks * self.event.talk_time)
