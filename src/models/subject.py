'''
Created on Nov 6, 2011

@author: averaart
'''

from google.appengine.ext import db

class Subject(db.Model):
    '''
    Subject-codes will be used as key_name
    '''
    name = db.StringProperty()