'''
Created on Oct 12, 2011

@author: averaart
'''

from google.appengine.ext import db

class Event(db.Model):
    '''
    Every series of parent-teacher nights is grouped in an Event 
    '''
    event_id = db.IntegerProperty()
    event_name = db.StringProperty()
    tables = db.IntegerProperty()
    talk_time = db.IntegerProperty()
    slots = db.IntegerProperty()
    start_time = db.DateTimeProperty()
    status = db.StringProperty()

