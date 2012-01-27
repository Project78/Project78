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

from classes.Email import Email

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

class AdministrationShowAppointmentHandler(webapp.RequestHandler):
    
    def get(self, arg):
        notifications = []
        path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-appointments.html')
        template_values = {
            'notifications': notifications, 
            'logoutlink': users.create_logout_url("/") 
        }
        self.response.out.write(template.render(path, template_values))
        return
    
    def post(self, arg):
        event = Event.get_by_id(int(arg))
        if not event:
            #todo
            '''event bestaat niet'''
            return
        
        code = self.request.POST['search-code']
        method = self.request.POST['search-on']
        
        if method == 'guardian':
            guardian = Guardian.get_by_key_name(code)
            if not guardian:
                print 'geen guardian met appointment'
            
            requests = guardian.all_requests.filter('event', event).fetch(999)
            appointments = [request.appointment.get() for request in requests]
            
            days = []
            for appointment in appointments:
                found = False
                for day in days:
                    if day.key().id() == appointment.day.key().id():
                        found = True
                        break
                if not found:
                    days.append(appointment.day)
            
            days_appointments = []
            for day in days:
                appointments_in_day = []
                for appointment in appointments:
                    if appointment.day.key().id() == day.key().id():
                        appointments_in_day.append(appointment)
                
                days_appointments.append([day, appointments_in_day])
            
            days_tables_appointments = []
            for day_appointments in days_appointments:
                tables = []
                for appointment in day_appointments[1]:
                    if appointment.table not in tables:
                        tables.append(int(appointment.table))
                
                day_tables = []
                for table in tables:
                    table_appointments = []
                    for appointment in day_appointments[1]:
                        if int(appointment.table) == table:
                            table_appointments.append(appointment)
                    day_tables.append([table, table_appointments])
                days_tables_appointments.append([day_appointments[0], day_tables])
                
            day_tables_slots = []
            for day_tables_appointments in days_tables_appointments:
                
                for table_appointments in day_tables_appointments[1]:
                    table_slots = []
                    for slot in range(1, day_tables_appointments[0].talks+1):
                        added = False
                        for appointment in table_appointments[1]:
                            if(int(appointment.slot) == slot):
                                added = True
                                table_slots.append(appointment)
                        if not added:
                            table_slots.append(1)
                    day_tables_slots.append([day_tables_appointments[0], [table_appointments[0], table_slots]])
        notifications = []
        path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-appointments.html')
        template_values = {
            'days': day_tables_slots,
            'notifications': notifications, 
            'logoutlink': users.create_logout_url("/") 
        }
        self.response.out.write(template.render(path, template_values))

class AdministrationInviteGuardiansHandler(webapp.RequestHandler):
    def get(self, arg):
        event = Event.get_by_id(int(arg))
        days = event.days
        
        subscriptions = SubscriptionDetails.all().filter('event', event).fetch(9999)
        mail = Email()
        for subscription in subscriptions:
            guardian = subscription.guardian
            message = 'Beste ' + guardian.title
            if not guardian.preposition == '':
                message += ' ' + guardian.preposition
            message += ' ' + guardian.lastname + ',\n\nOp'
            for day_num, day in enumerate(days):
                message += ' ' + str(day.date.day)
                if day_num < len(days.fetch(999)) - 1:
                    message += ','
            
            day = days.get()
            day.updateEndTime()
            message += ' ' + self.getMonthText(day.date.month) + ' ' + str(day.date.year) + ' zijn er weer mogelijkheden om met de docenten over de voortgang van uw zoon of dochter te praten. De avonden worden gehouden van ' + str(day.date.hour) + ':' + str(day.date.minute)
            if day.date.minute < 10:
                message += '0'
            message += ' tot ' + str(day.end_time.hour) + ':' + str(day.end_time.minute)
            if day.end_time.minute < 10:
                message += '0'
            message += '.\n\n'
            
            message += 'Per leerling kunt u tot drie vakken kiezen die u wilt bespreken.\n\n'
            
            message += 'Daarnaast kunt u de geplande avonden op volgorde van voorkeur zetten, en aangeven of u liever vroeger of later op de avond ingepland wil worden. Wij doen dan onze uiterste best om de gesprekken voor u zo gunstig mogelijk in te plannen. Houdt u er rekening mee dat in sommige gevallen niet aan alle voorkeuren voldaan zal kunnen worden.\n\n'
            
            message += 'U kunt zich inschrijven via http://www.donaldknuthcollege.nl/inschrijven met behulp van de volgende gegevens:\n'
            message += '- voogdnummer:\t' + str(guardian.key().name()) + '\n'
            message += '- sleutel:\t' + subscription.passphrase
            
            mail.sendMail(guardian.email, 'Uitnodiging ouderavond(en) ' + event.event_name, message)       
        
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
        
