'''
Created on Nov 5, 2011

@author: averaart
'''

from google.appengine.ext import db
from event import Event


class Teacher(db.Model):
    '''
    Teacher-codes will be used as key_name
    '''
    name = db.StringProperty()
    boxnumber = db.IntegerProperty()
    email = db.EmailProperty()

    def isFull(self, event):
        slots = 0
        for day in event.days:
            slots += day.talks
        subjects = self.subjects.fetch(9999)
        requests = []
        for subject in subjects:
            requests.append(subject.requests.filter("event", event).fetch(9999))
        if len(requests) >= slots:
            return True
        else:
            return False
        