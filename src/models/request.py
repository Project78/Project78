'''
Created on Nov 6, 2011

@author: averaart
'''

from google.appengine.ext import db
from event import Event
from guardian import Guardian
from student import Student
from combination import Combination

class Request(db.Model):
    '''
    A Request represents one subject about which a Guardian wants to talk
    '''
    event = db.ReferenceProperty(Event, collection_name="requests")
    guardian = db.ReferenceProperty(Guardian, collection_name="requests")
    student = db.ReferenceProperty(Student, collection_name="requests")
    combination = db.ReferenceProperty(Combination, collection_name="requests")