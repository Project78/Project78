'''
Created on Oct 12, 2011

@author: averaart
'''

from google.appengine.ext import db

class Guardian(db.Model):
    '''
    For all students, one parent (or guardian) will be registered
    '''
    title = db.StringProperty()
    initials = db.StringProperty()
    preposition = db.StringProperty()
    lastname = db.StringProperty()
    streetname = db.StringProperty()
    housenumber = db.StringProperty()
    city = db.StringProperty()
    postalcode = db.StringProperty()
    email = db.EmailProperty()
