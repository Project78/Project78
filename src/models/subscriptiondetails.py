'''
Created on Jan 26, 2012

@author: Maarten
'''
from datetime import timedelta
from google.appengine.ext import db
from event import Event
from guardian import Guardian

class SubscriptionDetails(db.Model):
    '''
    Each SubscriptionDetail has a unique key and a status
    '''
    passphrase = db.StringProperty()
    event = db.ReferenceProperty(Event) 
    guardian = db.ReferenceProperty(Guardian)
    requested = db.BooleanProperty()
