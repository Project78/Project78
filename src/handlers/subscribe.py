import os
import re
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
from models.combination import Combination
from models.request import Request
from models.subject import Subject
from models.timepreference import TimePreference
from models.daypreference import DayPreference

class Subscribe(webapp.RequestHandler):
#        /inschrijven/1285/1111

    #@todo: authorization ok?
    #@todo: is it already filled in?
    #@todo: max number per student ok?
    #@todo: does event exist?
    #@todo: does guardian exists?
    #@todo: has the guardian the right students?
    #@todo: how do users log in?
    #@todo: does subject code exist?
    #@todo: where to go after good post?
    #@todo: where to go after error?
    #@todo: time pref ok?
    #@todo: day pref ok?

    def get(self, eventId, guardianId):
        event = Event.get_by_id(int(eventId))
        days = Day.gql("WHERE event = :1", event).fetch(999)
        guardian = Guardian.get_by_key_name(guardianId)
        students = Student.gql("WHERE guardian = :1", guardian).fetch(999, 0)

        students_subjects = [] 
        for student in students:
            class_id = student.class_id 
            combinations = Combination.gql("WHERE class_id = :1", class_id).fetch(10, 0)
            subjects = []
            for combination in combinations:
                subjects.append(combination.subject)
            students_subjects.append([student, subjects])

        if event and guardian and students and days:
            templVal = {
                'event': event,
                'days': days,
                'guardian': guardian,
                'students': students_subjects
            }
            path = os.path.join(os.path.dirname(__file__), '../templates/subscription.html')
            self.response.out.write(template.render(path, templVal))
        
        
    def post(self, eventId, guardianId):
        event = Event.get_by_id(int(eventId))
        days = Day.gql("WHERE event = :1", event).fetch(999)
        guardian = Guardian.get_by_key_name(guardianId)
        students = Student.gql("WHERE guardian = :1", guardian).fetch(999, 0)
        studentKeys = [str(k.replace('subject_', '')) for k in self.request.arguments() if re.match("subject_.+", k)]
        requests = []
        dayPrefs = []
        
        for s in students[:]:
            if str(s.key().name()) not in studentKeys:
                students.remove(s)
        for student in students[:]:
            subjectCodes = [c for c in self.request.get_all("subject_" + str(student.key().name()))]
            subjects = Subject.get_by_key_name(subjectCodes)
            for subject in subjects:
                combination = Combination.gql("WHERE class_id = :1 AND subject = :2", student.class_id, subject).fetch(1,0)[0]
                request = Request()
                request.event = event
                request.guardian = guardian
                request.student = student
                request.combination = combination
                requests.append(request)
        
        
        timePref = TimePreference()
        timePref.event = event
        timePref.guardian = guardian
        timePref.preference = 0
        if self.request.get('time_pref') and (int(self.request.get('time_pref')) in [0,1,2]):
            timePref.preference = int(self.request.get('time_pref'))
        
        
        dayKeys = [long(k.replace('date_', '')) for k in self.request.arguments() if re.match("date_.+", k)]
        dayKeysFromStore= [day.key().id() for day in days]
        daysOk = True
        for dayKey in dayKeys:
            if dayKey not in dayKeysFromStore:
                daysOk = False
                break
        dayPrefsList = [int(self.request.get(k)) for k in self.request.arguments() if re.match("date_.+", k)]
        dayPrefsList.sort()
        dayPrefsOk = False
        if dayPrefsList == [1,2,3]:
            dayPrefsOk = True
        
        if daysOk and dayPrefsOk:
            for day in days:
                print 'day number'
                dayPref = DayPreference()
                dayPref.day = day
                dayPref.guardian = guardian
                dayPref.rank = int(self.request.get("date_" + str(day.key().id())))
                dayPrefs.append(dayPref)
                
#                print dayPref.day
#                print dayPref.guardian
#                print dayPref.rank

        for request in requests:
            request.put()
        for dayPref in dayPrefs:
            dayPref.put()
        timePref.put()
        


    
