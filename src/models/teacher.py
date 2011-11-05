'''
Created on Nov 5, 2011

@author: averaart
'''

from google.appengine.ext import db

class Teacher(db.Model):
    '''
    Teacher-codes will be used as key_name
    '''
    name = db.StringProperty()
    boxnumber = db.IntegerProperty()
    email = db.EmailProperty()
