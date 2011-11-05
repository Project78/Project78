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
import cgi
import csv
import datetime
import math

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from google.appengine.api.datastore import Key

from models.day import Day
from models.daypreference import DayPreference
from models.event import Event
from models.guardian import Guardian
from models.student import Student
from models.teacher import Teacher
from models.timepreference import TimePreference

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
            new_day_preference.guardian_id =  Guardian.all().filter("guardian_id =", int(self.request.get("guardian_id"))).get() 
            new_day_preference.save()
            new_days.append(new_day_preference)
        new_days.sort(key=lambda day: day.rank)
        
        # Build new time_preference
        new_time_preference = TimePreference()
        new_time_preference.guardian_id =  Guardian.all().filter("guardian_id =", int(self.request.get("guardian_id"))).get()
        new_time_preference.event_id = Event.all().filter("event_id =", int(self.request.get("event_id"))).get()
        new_time_preference.time_pref = int(self.request.get("time_pref"))
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


class AdministrationHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/administration/event-new.html')
        template_values = {
        }
        self.response.out.write(template.render(path, template_values))
    
    def post(self):
        a = self.request.POST['event-date']
        a = [1, 2, 3, 4]
        self.response.out.write("<table>")
        for key, value in self.request.POST.iteritems():
            self.response.out.write("<tr><td>" + key + "</td><td>" + value + "</td></tr>")
        self.response.out.write("</table>")

class EventHandler(webapp.RequestHandler):
    def get(self):
        events = Event.all()
        days = []
        for event in events:
            retrievedDays = Day.gql("WHERE event = :1", event)
            for day in retrievedDays:
                hours = day.date.hour
                minutes = day.date.minute
                if day.talks != None:
                    minutes += day.talks * event.talk_time
                    
                if minutes >= 60:
                    hours += int(math.floor(minutes / 60))
                    minutes %= 60
                day.end_time = datetime.datetime(year=day.date.year, month=day.date.month, day=day.date.day, hour=hours, minute=minutes)
                day.put()
            days.extend(retrievedDays)
        path = os.path.join(os.path.dirname(__file__), 'templates/administration/event-overview.html')
        template_values = {
            'events': events,
            'days': days         
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
        new_event = Event(event_id=1,
                          tables=40,
                          talk_time=15)
        new_event.put()

        # Add some days to the aforementioned event
        new_day = Day(day_id=1,
                      date=datetime.datetime(year=2011, month=11, day=11, hour=20, minute=00),
                      talks=12,
                      event=new_event)
        new_day.put()

        new_day = Day(day_id=2,
                      date=datetime.datetime(year=2011, month=11, day=12, hour=20, minute=00),
                      talks=12,
                      event=new_event)
        new_day.put()

        new_day = Day(day_id=3,
                      date=datetime.datetime(year=2011, month=11, day=13, hour=20, minute=00),
                      talks=12,
                      event=new_event)
        new_day.put()
        
        # Add an event
        new_event = Event(event_id=2,
                          tables=40,
                          talk_time=15)
        new_event.put()

        # Add some days to the aforementioned event
        new_day = Day(day_id=4,
                      date=datetime.datetime(year=2011, month=11, day=20, hour=19, minute=30),
                      talks=12,
                      event=new_event)
        new_day.put()

        new_day = Day(day_id=5,
                      date=datetime.datetime(year=2011, month=11, day=21, hour=20, minute=00),
                      talks=12,
                      event=new_event)
        new_day.put()

        new_day = Day(day_id=6,
                      date=datetime.datetime(year=2011, month=11, day=22, hour=19, minute=45),
                      talks=12,
                      event=new_event)
        new_day.put()

class InitDataHandler(webapp.RequestHandler):
    def get(self):
        
#        # Load all Guardians
#        path = os.path.join(os.path.dirname(__file__), 'data/voogdouder.csv')
#        my_file = open(path)
#        fileReader = csv.reader(my_file) 
#        for row in fileReader: 
#            my_list = row[0].split(' ; ')
#            new_guardian = Guardian(key_name=my_list[0])
#            new_guardian.title=my_list[1]
#            new_guardian.initials=my_list[2]
#            new_guardian.preposition=my_list[3]
#            new_guardian.lastname=my_list[4]
#            new_guardian.streetname=my_list[6]
#            new_guardian.housenumber=my_list[7]
#            new_guardian.city=my_list[8]
#            new_guardian.postalcode=my_list[9]
#            new_guardian.email=my_list[12]
#            new_guardian.save()
#
#        # Load all Students
#        path = os.path.join(os.path.dirname(__file__), 'data/leerlingen.csv')
#        my_file = open(path)
#        fileReader = csv.reader(my_file) 
#        for row in fileReader: 
#            my_list = row[0].split(' ; ')
#            new_student = Student(key_name=my_list[0])
#            new_student.firstname=my_list[1]
#            new_student.preposition=my_list[2]
#            new_student.lastname=my_list[3]
#            new_student.gender=my_list[4]
#            new_student.class_id=my_list[5]
#            new_student.guardian=Guardian.all().filter("__key__ >=", Key.from_path('Guardian', my_list[6])).get()
#            new_student.save()

        # Load all Teachers
        path = os.path.join(os.path.dirname(__file__), 'data/docenten.csv')
        my_file = open(path)
        fileReader = csv.reader(my_file) 
        for row in fileReader:
            my_list = row[0].split(' ; ')
            
            print my_list[0]
            new_teacher = Teacher(key_name=my_list[0])
            new_teacher.name=my_list[1]
            new_teacher.boxnumber=int(my_list[2], 0)
#            new_teacher.email=my_list[3]
#            new_teacher.save()



def main():
    application = webapp.WSGIApplication([('/', IndexHandler),
                                          ('/inschrijven', RegisterHandler),
                                          ('/inschrijvingen', ListRegistrationsHandler),
                                          ('/fill', FillDatabaseHandler),
                                          ('/init', InitDataHandler),
                                          ('/administratie', EventHandler),
                                          ('/administratie/nieuw-event', AdministrationHandler)
                                          ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
