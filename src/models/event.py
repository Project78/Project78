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
    tables = db.IntegerProperty()
    talk_time = db.IntegerProperty()
    
