'''
Created on Oct 12, 2011

@author: averaart
'''

from google.appengine.ext import db

class Guardian(db.Model):
    '''
    For all students, one parent (or guardian) will be registered
    '''
    guardian_id = db.IntegerProperty()
    firstname = db.StringProperty()
    preposition = db.StringProperty()
    lastname = db.StringProperty()
