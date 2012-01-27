'''
Created on Jan 26, 2012

@author: Maarten
'''
import os
import datetime
import re
import binascii

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from models.event import Event
from models.day import Day
from models.guardian import Guardian
from models.subscriptiondetails import SubscriptionDetails
from copy import deepcopy

class AdministrationIndexHandler(webapp.RequestHandler):

    def get(self):
        path = os.path.join(os.path.dirname(__file__), '../templates/administration/administration-index.html')
        template_values = {'logoutlink': users.create_logout_url("/") }
        self.response.out.write(template.render(path, {template_values}))

class AdministrationEventListHandler(webapp.RequestHandler):
    
    def get(self):
        events = Event.all()
        path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-list.html')
        template_values = {'events': events, 'logoutlink': users.create_logout_url("/") }
        self.response.out.write(template.render(path, template_values))

class AdministrationEventEditHandler(webapp.RequestHandler):
    
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
                'monthText': monthText,
                'logoutlink': users.create_logout_url("/")         
            }
            path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-edit.html')
            self.response.out.write(template.render(path, tV))
        
        #first call of new event
        elif arg == 'nieuw':
            path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-edit.html')
            self.response.out.write(template.render(path, {'logoutlink': users.create_logout_url("/")}))
            
            
    def post(self, arg):
        if self.request.POST['i-save-event']:
            n = self.request.POST['i-name']
            d = self.request.POST['i-startdate']
            v = Validator()
            errors = [];

            #is it an existing event or not?    
            if arg.isdigit():
                nE = Event.get_by_id(int(arg))
                nDs = Day.gql("WHERE event = :1", nE).fetch(3) 
            elif arg == 'nieuw':
                nE = Event(tables=40, talk_time=15)
                nDs = [Day(talks=12), Day(talks=12), Day(talks=12)]
            
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
                nDs[0].date = sD
                
            #show errors if they exist
            if errors:
                path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-edit.html')
                monthText = ''
                if nDs[0].date:
                    monthText = self.getMonthText(nDs[0].date.month)
                
                tv = { 
                      'errors': errors,
                      'event': nE,
                      'day': nDs[0],
                      'monthText': monthText,
                      'logoutlink': users.create_logout_url("/")  
                }
                self.response.out.write(template.render(path, tv))
            
            #update event in datastore if no error exists
            else:
                nE.put()
                #add two other dates and store them
                delta = datetime.timedelta(days=1)
                if nDs[0].date.weekday() < 3:
                    nDs[1].date = deepcopy(nDs[0].date) + delta
                    nDs[2].date = deepcopy(nDs[0].date) + delta*2
                elif nDs[0].date.weekday() == 3:
                    nDs[1].date = deepcopy(nDs[0].date) + delta
                    nDs[2].date = deepcopy(nDs[0].date) + delta*3
                elif nDs[0].date.weekday() == 4:
                    nDs[1].date = deepcopy(nDs[0].date) + delta*3
                    nDs[2].date = deepcopy(nDs[0].date) + delta*4
                    
                for d in nDs:
                    d.event = nE
                    d.updateEndTime()
                    d.put()
                
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

class AdministrationGenerateGuardianKeys(webapp.RequestHandler):
    
    def get(self, arg):
        event = Event.get_by_id(int(arg))
        notifications = []
        events = Event.all()
        path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-list.html')
        template_values = {
            'notifications': notifications, 
            'events': events, 
            'logoutlink': users.create_logout_url("/") 
        }
        if not event:
            notifications.append('Het event bestaat niet.')
            self.response.out.write(template.render(path, template_values))
            return
        
        self.createGuardianPasses(event)
        notifications.append('De sleutels zijn aangemaakt')
        self.response.out.write(template.render(path, template_values))
        return
        
    def createGuardianPasses(self, event):
        for g in Guardian.all():
            sD = SubscriptionDetails()
            sD.event = event
            sD.guardian = g
            sD.requested = False
            sD.passphrase = binascii.b2a_hex(os.urandom(15))
            sD.put()

class AdministrationInviteGuardiansHandler(webapp.RequestHandler):
    
    def get(self, arg):
        return     
    
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
        
