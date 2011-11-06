'''
Created on Nov 6, 2011

@author: averaart
'''

from google.appengine.ext import db
from teacher import Teacher
from subject import Subject

class Combination(db.Model):
    '''
    Teacher-codes will be used as key_name
    '''
    class_id = db.StringProperty()
    subject = db.ReferenceProperty(Subject, collection_name="teacher")
    teacher = db.ReferenceProperty(Teacher, collection_name="subject")
