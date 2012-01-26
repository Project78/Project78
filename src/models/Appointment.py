'''
Created on Jan 26, 2012

@author: averaart
'''

from google.appengine.ext import db
from event import Event
from guardian import Guardian
from student import Student
from combination import Combination
from day import Day

class Appointment(db.Model):
    '''
    Each talk between a teacher and a guardian is a new Appointment 
    '''
    event = db.ReferenceProperty(Event, collection_name="appointments")
    guardian = db.ReferenceProperty(Guardian, collection_name="appointments")
    student = db.ReferenceProperty(Student, collection_name="appointments")
    combination = db.ReferenceProperty(Combination, collection_name="appointments")
    day = db.ReferenceProperty(Day, collection_name="appointments")
    table = db.IntegerProperty()
    slot = db.IntegerProperty()