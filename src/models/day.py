'''
Created on Oct 12, 2011

@author: averaart
'''

from google.appengine.ext import db
from event import Event

class Day(db.Model):
    '''
    Every Event is divided into Days 
    '''
    day_id = db.IntegerProperty()
    date = db.DateTimeProperty()
    talks = db.IntegerProperty()
    event = db.ReferenceProperty(Event, collection_name="days")
    end_time = db.DateTimeProperty()
    