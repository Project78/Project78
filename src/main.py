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
import datetime
import math

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

from models.day import Day
from models.daypreference import DayPreference
from models.event import Event
from models.guardian import Guardian
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
#        response = self.request.arguments()
#        for arg in response:
#            if "day_" in arg:
#                print arg +" - "+ self.request.get(arg)

        path = os.path.join(os.path.dirname(__file__), 'templates/eventformresponse.html')
        template_values = {
            'guardian_id': cgi.escape(self.request.get('guardian_id')),
            'day_id': cgi.escape(self.request.get('day_id')),
            'rank': cgi.escape(self.request.get('rank')),
        }
        self.response.out.write(template.render(path, template_values))


class ListRegistrationsHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/listregistrations.html')
        template_values = {
            'greetings': "Hi"
        }
        self.response.out.write(template.render(path, template_values))


class AdministrationHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/administration/event-new.html')
        template_values = {
        }
        self.response.out.write(template.render(path, template_values))

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

def main():
    application = webapp.WSGIApplication([('/', IndexHandler),
                                          ('/inschrijven', RegisterHandler),
                                          ('/inschrijvingen', ListRegistrationsHandler),
                                          ('/fill', FillDatabaseHandler),
                                          ('/administratie', EventHandler),
                                          ('/administratie/nieuw-event', AdministrationHandler)
                                          ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
