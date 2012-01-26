'''
Created on Jan 26, 2012

@author: averaart
'''

from google.appengine.ext import db
from request import Request
from day import Day

class Appointment(db.Model):
    '''
    Each talk between a teacher and a guardian is a new Appointment 
    '''
    request = db.ReferenceProperty(Request, collection_name="appointment")
    day = db.ReferenceProperty(Day, collection_name="appointments")
    table = db.IntegerProperty()
    slot = db.IntegerProperty()