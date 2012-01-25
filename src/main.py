#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import fnmatch
import cgi
import csv
import datetime
import math
import random
import time
import copy

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from google.appengine.api.datastore import Key
from google.appengine.ext import db

from models.event import Event
from models.day import Day
from models.daypreference import DayPreference
from models.timepreference import TimePreference
from models.guardian import Guardian
from models.student import Student
from models.teacher import Teacher
from models.subject import Subject
from models.combination import Combination
from models.request import Request
from handlers.newevent import NewEvent
from handlers.editevent import EditEvent
from handlers.plan import plan
from handlers.test import test
from handlers.fixteachers import FixTeachers
from handlers.mailevent import MailHandler



class IndexHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        template_values = {
            'greetings': "Hi"
        }
        self.response.out.write(template.render(path, template_values))

class RegisterHandler(webapp.RequestHandler):
    def get(self):
        guardian = Guardian.gql("WHERE guardian_id = :1", 6781)
        current_event = Event.gql("WHERE event_id = :1", 1)
        event_days = Day.gql("WHERE event = :1",current_event[0])
            
        path = os.path.join(os.path.dirname(__file__), 'templates/eventform.html')
        template_values = {
            'guardian': guardian[0],
            'event': current_event[0],
            'days': event_days
        }
        self.response.out.write(template.render(path, template_values))
    
    def post(self):
        # Pull in all POST arguments
        params = {}
        for field in self.request.arguments():
            params[field] = self.request.get(field)
        
        # Filter out ranking info for days            
        days = {}
        for key, value in params.items():
            if not key.find("day_"):
                days[key.replace("day_", "")] = value
        
        # Build new day_preference entities
        new_days = []
        for day, rank in days.items():
            new_day_preference = DayPreference()
            new_day_preference.day = Day.all().filter("day_id =", int(day)).get()
            new_day_preference.rank = int(rank)
            new_day_preference.guardian =  Guardian.all().filter("guardian_id =", int(self.request.get("guardian_id"))).get() 
            new_day_preference.save()
            new_days.append(new_day_preference)
        new_days.sort(key=lambda day: day.rank)
        
        # Build new time_preference
        new_time_preference = TimePreference()
        new_time_preference.guardian =  Guardian.all().filter("guardian_id =", int(self.request.get("guardian_id"))).get()
        new_time_preference.event = Event.all().filter("event_id =", int(self.request.get("event_id"))).get()
        new_time_preference.preference = int(self.request.get("time_pref"))
        new_time_preference.save()
        

        path = os.path.join(os.path.dirname(__file__), 'templates/eventformresponse.html')
        template_values = {
            'days': new_days,
            'time': new_time_preference
        }
        self.response.out.write(template.render(path, template_values))


class ListRegistrationsHandler(webapp.RequestHandler):
    def get(self):
        
        events = Event.all().fetch(100)
        
        path = os.path.join(os.path.dirname(__file__), 'templates/listregistrations.html')
        template_values = {
            'events': events
        }
        self.response.out.write(template.render(path, template_values))

class EventHandler(webapp.RequestHandler):
    def get(self):
        events = Event.all()
        path = os.path.join(os.path.dirname(__file__), 'templates/administration/event-list.html')
        template_values = {
            'events': events      
        }
        self.response.out.write(template.render(path, template_values))

class FillDatabaseHandler(webapp.RequestHandler):
    def get(self):
        
        # Add some guardians
        new_guardian = Guardian(guardian_id=6781,
                                firstname="A.J.",
                                preposition="van",
                                lastname="Brandsma")
        new_guardian.put()

        new_guardian = Guardian(guardian_id=6900,
                                firstname="M.",
                                lastname="Tervuure")
        new_guardian.put()
        
        # Add an event
        new_event = Event(tables=40,
                          talk_time=15)
        new_event.put()

        # Add some days to the aforementioned event
        new_day = Day(date=datetime.datetime(year=2011, month=11, day=11, hour=20, minute=00),
                      talks=12,
                      event=new_event)
        new_day.put()

        new_day = Day(date=datetime.datetime(year=2011, month=11, day=12, hour=20, minute=00),
                      talks=12,
                      event=new_event)
        new_day.put()

        new_day = Day(date=datetime.datetime(year=2011, month=11, day=13, hour=20, minute=00),
                      talks=12,
                      event=new_event)
        new_day.put()
        
        # Add an event
        new_event = Event(tables=40,
                          talk_time=15)
        new_event.put()

        # Add some days to the aforementioned event
        new_day = Day(date=datetime.datetime(year=2011, month=11, day=20, hour=19, minute=30),
                      talks=12,
                      event=new_event)
        new_day.put()

        new_day = Day(date=datetime.datetime(year=2011, month=11, day=21, hour=20, minute=00),
                      talks=12,
                      event=new_event)
        new_day.put()

        new_day = Day(date=datetime.datetime(year=2011, month=11, day=22, hour=19, minute=45),
                      talks=12,
                      event=new_event)
        new_day.put()

class InitDataHandler(webapp.RequestHandler):
    def get(self):
        
        # Load all Guardians
        path = os.path.join(os.path.dirname(__file__), 'data/voogdouder.txt')
        my_file = open(path)
        fileReader = csv.reader(my_file, delimiter=";") 
        for row in fileReader: 
            new_guardian = Guardian(key_name=row[0].strip())
            new_guardian.title=row[1].strip()
            new_guardian.initials=row[2].strip()
            new_guardian.preposition=row[3].strip()
            new_guardian.lastname=row[4].strip()
            new_guardian.streetname=row[6].strip()
            new_guardian.housenumber=row[7].strip()
            new_guardian.city=row[8].strip()
            new_guardian.postalcode=row[9].strip()
            new_guardian.email=row[12].strip()
            new_guardian.save()
            print "Guardian " + new_guardian.key().id_or_name() + " stored"

        # Load all Students
        path = os.path.join(os.path.dirname(__file__), 'data/leerlingen.txt')
        my_file = open(path)
        fileReader = csv.reader(my_file, delimiter=";") 
        for row in fileReader: 
            new_student = Student(key_name=row[0].strip())
            new_student.firstname=row[1].strip()
            new_student.preposition=row[2].strip()
            new_student.lastname=row[3].strip()
            new_student.gender=row[4].strip()
            new_student.class_id=row[5].strip()
            new_student.guardian=Guardian.all().filter("__key__ >=", Key.from_path('Guardian', row[6].strip())).get()
            new_student.save()
            print "Student " + new_student.key().id_or_name() + " stored"
            
        # Load all Teachers
        path = os.path.join(os.path.dirname(__file__), 'data/docenten.txt')
        my_file = open(path)
        fileReader = csv.reader(my_file, delimiter=";") 
        for row in fileReader:
            new_teacher = Teacher(key_name=row[0].strip())
            new_teacher.name=row[1].strip()
            new_teacher.boxnumber=int(row[2].strip())
            new_teacher.email=row[3].strip()
            new_teacher.save()
            print "Teacher " + new_teacher.key().id_or_name() + " stored"
            
        # Load all Subjects
        path = os.path.join(os.path.dirname(__file__), 'data/vakken.txt')
        my_file = open(path)
        fileReader = csv.reader(my_file, delimiter=";") 
        for row in fileReader:
            new_subject = Subject(key_name=row[0].strip())
            new_subject.name=row[1].strip()
            new_subject.save()
            print "Subject " + new_subject.key().id_or_name() + " stored"

        # Load all Students
        path = os.path.join(os.path.dirname(__file__), 'data/docent_vak.txt')
        my_file = open(path)
        fileReader = csv.reader(my_file, delimiter=";") 
        for row in fileReader: 
            new_combination = Combination()
            new_combination.class_id=row[0].strip()
            new_combination.subject=Subject.all().filter("__key__ >=", Key.from_path('Subject', row[1].strip())).get()
            new_combination.teacher=Teacher.all().filter("__key__ >=", Key.from_path('Teacher', row[2].strip())).get()
            new_combination.save()
            print "Combination " + str(new_combination.key().id_or_name()) + " stored"
        self.redirect("/fix")

class GenerateRandomEventHandler(webapp.RequestHandler):
    def get(self):
        
        try:
            while True:
                q = db.GqlQuery("SELECT __key__ FROM DayPreference")
                assert q.count()
                db.delete(q.fetch(500))
                time.sleep(0.1)
        except Exception, e:
            pass

        try:
            while True:
                q = db.GqlQuery("SELECT __key__ FROM TimePreference")
                assert q.count()
                db.delete(q.fetch(500))
                time.sleep(0.1)
        except Exception, e:
            pass
        
        try:
            while True:
                q = db.GqlQuery("SELECT __key__ FROM Request")
                assert q.count()
                db.delete(q.fetch(500))
                time.sleep(0.1)
        except Exception, e:
            pass
        
        try:
            while True:
                q = db.GqlQuery("SELECT __key__ FROM Day")
                assert q.count()
                db.delete(q.fetch(500))
                time.sleep(0.1)
        except Exception, e:
            pass
        
        try:
            while True:
                q = db.GqlQuery("SELECT __key__ FROM Event")
                assert q.count()
                db.delete(q.fetch(500))
                time.sleep(0.1)
        except Exception, e:
            pass
        
        
        # Set random seed
        random.seed(1138)
                
        # Add an event
        event = Event(event_name="paasrapport",
                      tables=10,
                      talk_time=15)
        event.put()

        # Add some days to the aforementioned event
        day = Day(date=datetime.datetime(year=2011, month=11, day=11, hour=20, minute=00),
                      talks=7,
                      event=event)
        day.put()

#        day = Day(date=datetime.datetime(year=2011, month=11, day=12, hour=20, minute=00),
#                      talks=12,
#                      event=event)
#        day.put()
#
#        day = Day(date=datetime.datetime(year=2011, month=11, day=13, hour=20, minute=00),
#                      talks=12,
#                      event=event)
#        day.put()
        
        guardians = Guardian.all().fetch(40)
        for guardian in guardians:
            time = TimePreference()
            time.event = event
            time.guardian = guardian
            time.preference = random.randint(0, 2)
            time.save()
            days = event.days.fetch(999)
            random.shuffle(days)
            for i, day in enumerate(days):
                day_pref = DayPreference()
                day_pref.guardian = guardian
                day_pref.day = day
                day_pref.rank = i
                day_pref.save()
            for child in guardian.children:
                subjects = Combination.all().filter('class_id', child.class_id).fetch(999)
#                slots = 0
#                for day in event.days:
#                    slots += day.talks
#                print ""
#                print slots
#                
#                print len(subjects)
#                
#                for comb in subjects:
#                    if comb.teacher.isFull(event):
#                        print "Leraar heeft al genoeg verzoeken."
#                        subjects.remove(comb)
                selection = random.sample(subjects, int(random.triangular(0, 4, 0)))
#                
#                print len(subjects)
                
                for choice in selection:
                    request = Request()
                    request.event = event
                    request.guardian = guardian
                    request.student = child
                    request.combination = choice
                    request.save()
                    

                    
class DisplayRequestsHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/requests.html')
        template_values = {
            'event': Event.all().filter('event_name', 'paasrapport').fetch(1),
            'guardians': Guardian.all().fetch(9999)
        }
        self.response.out.write(template.render(path, template_values))        
    
class bulkdelete(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        path = "models"
        dirList = os.listdir(path)
        for fname in dirList:
            if fnmatch.fnmatch(fname, '*.py') and not fnmatch.fnmatch(fname, '_*'):
                try:
                    while True:
                        q = db.GqlQuery("SELECT __key__ FROM " + fname.capitalize().split('.')[0].replace('preference', 'Preference'))
                        assert q.count()
                        db.delete(q.fetch(200))
                        time.sleep(0.5)
                except Exception, e:
                    self.response.out.write(repr(e)+'\n')
                    pass

def main():
    application = webapp.WSGIApplication([('/', IndexHandler),
                                          ('/inschrijven', RegisterHandler),
                                          ('/inschrijvingen', ListRegistrationsHandler),
                                          ('/fill', FillDatabaseHandler),
                                          ('/init', InitDataHandler),
                                          ('/generate', GenerateRandomEventHandler),
                                          ('/plan', plan),
                                          ('/test', test),
                                          ('/fix', FixTeachers),
                                          ('/requests', DisplayRequestsHandler),
                                          ('/administratie', EventHandler),
                                          ('/clear', bulkdelete),
                                          ('/administratie/event/(nieuw|\d+)', EditEvent),
                                          ('/mail', MailHandler)
                                          ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
