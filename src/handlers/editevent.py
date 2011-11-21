import os
import math
import datetime
import re

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from models.event import Event
from models.day import Day

class EditEvent(webapp.RequestHandler):
    
    def get(self, arg):
        #first call for edit modus
        if arg.isdigit():
            #get event info and parse it in template
            event = Event.get_by_id(int(arg))
            day = Day.gql("WHERE event = :1", event)[0]
            monthText = self.getMonthText(day.date.month)
            tV = {
                'event': event,
                'day': day,
                'monthText': monthText         
            }
                        
            path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-edit.html')
            self.response.out.write(template.render(path, tV))
        
        #first call of new event
        elif arg == 'nieuw':
            path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-edit.html')
            self.response.out.write(template.render(path, {}))
            
            
    def post(self, arg):
#        if self.request.POST['i-delete-event']:
#            print 'delete'
        if self.request.POST['i-save-event']:
            #check if ok
            #collect erros
            n = self.request.POST['i-name']
            d = self.request.POST['i-startdate']
            v = Validator()
            errors = [];
    
    
            if arg.isdigit():
                nE = Event.get_by_id(int(arg))
                nD = Day.gql("WHERE event = :1", nE)[0]
            elif arg == 'nieuw':
                nE = Event(tables=40, talk_time=15)
                nD = Day(talks=12)
            
            #validate data
            if not v.vString(n):
                errors.append('onjuiste titel ouderavondreeks')
            else:
                nE.event_name = n    
            if not v.vDate(d):
                errors.append('onjuiste startdatum')
            else:
                d = map(int, (d.split('-')))
                sD = datetime.datetime(year=d[0], month=d[1], day=d[2], hour=20, minute=00)
                nD.date = sD
    
            #show errors if they exist
            if errors:
                path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-edit.html')
                monthText = ''
                if nD.date:
                    monthText = self.getMonthText(nD.date.month)
                
                tv = { 
                      'errors': errors,
                      'event': nE,
                      'day': nD,
                      'monthText': monthText  
                }
                self.response.out.write(template.render(path, tv))
            #update event in datastore if no error exists
            else:
                nE.put()
                nD.event = nE
                nD.put()
                self.redirect('/administratie')
        
    def getMonthText(self, i):
        return {
            1: 'januari',
            2: 'februari',
            3: 'maart',
            4: 'april',
            5: 'mei',
            6: 'juni',
            7: 'juli',
            8: 'augustus',
            9: 'september',
            10: 'oktober',
            11: 'november',
            12: 'december'
        }.get(i, '')  


class Validator:
    def vDate(self, d):
        if re.match(r'\d{4}-\d{2}-\d{2}', d):
            return True
        else:
            return False
    
    def vString(self, s):
        if s:
            return True
        else:
            return False
        
