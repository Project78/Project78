'''
Created on Nov 5, 2011

@author: averaart
'''

from google.appengine.ext import db
from guardian import Guardian

class Student(db.Model):
    '''
    All Students should reference a Guardian
    '''
    firstname = db.StringProperty()
    preposition = db.StringProperty()
    lastname = db.StringProperty()
    gender = db.StringProperty()
    class_id = db.StringProperty()
    guardian = db.ReferenceProperty(Guardian, collection_name="children")
