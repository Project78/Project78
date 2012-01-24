import os
'''
Created on Dec 19, 2011

@author: Maarten van den Hoek
'''

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from models.guardian import Guardian
from models.event import Event
from models.student import Student
from models.day import Day

class Subscribe(webapp.RequestHandler):
#        /inschrijven/190/1111



    def get(self, eventId, guardianId):
        
        event = Event.get_by_id(int(eventId))
        days = Day.gql("WHERE event = :1", event).fetch(1, 0)
        guardian = Guardian.get_by_key_name(guardianId)
        students = Student.gql("WHERE guardian = :1", guardian).fetch(15, 0)
        #students_subjects = null
        
        if event and guardian and students and days:
            
            templVal = {
                'event': event,
                'days': days,
                'guardian': guardian,
                'students': students
            }
            path = os.path.join(os.path.dirname(__file__), '../templates/subscription.html')
            self.response.out.write(template.render(path, templVal))
        
        return
        
        
    def post(self, arg):
        return

    
