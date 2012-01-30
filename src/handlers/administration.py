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
from datetime import timedelta
from models.event import Event
from models.day import Day
from models.guardian import Guardian
from models.teacher import Teacher
from models.request import Request
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
        event = Event.get_by_id(int(arg))
        notifications = []
        if not event:
            notifications.append("Er is geen ouderavondreeks gevonden met het nummer " + str(arg))
        path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-appointments.html')
        template_values = {
            'event': event,
            'notifications': notifications, 
            'logoutlink': users.create_logout_url("/")
        }
        self.response.out.write(template.render(path, template_values))
        return
    
    def post(self, arg):
        event = Event.get_by_id(int(arg))
        notifications = []
        appointments = []
        
        template_values = {
            'event': event,
            'appointments': appointments,
            'notifications': notifications, 
            'logoutlink': users.create_logout_url("/") 
        }
        
        if not event: 
            notifications.append("Er is geen ouderavondreeks gevonden met het nummer " + str(arg))
            path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-appointments.html')
            self.response.out.write(template.render(path, template_values))
            return
        
        code = self.request.POST['search-code']
        method = self.request.POST['search-on']
        
        if not code:
            notifications.append("Er dient een docentcode of voogdnummer ingevoerd te worden.")
        if not method:
            notifications.append("Er dient aangegeven te worden of er op docent of voogd gezocht wordt.")
        if not (code and method):
            path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-appointments.html')
            self.response.out.write(template.render(path, template_values))
            return
        
        if method == 'guardian':
            guardian = Guardian.get_by_key_name(code)
            if not guardian:
                notifications.append("Er is geen voogd gevonden met het voogdnummer " + str(code))
                path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-appointments.html')
                self.response.out.write(template.render(path, template_values))
                return
            
            requests = guardian.all_requests.filter('event', event).fetch(999)
            for request in requests: 
                if request.appointment.get():
                    appointments.append(request.appointment.get()) 
            
            if not appointments:
                notifications.append("Er zijn geen afspraken gevonden voor de voogd met het voogdnummer " + str(code))
                path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-appointments.html')
                self.response.out.write(template.render(path, template_values))
                return
            
#            days = []
#            for appointment in appointments:
#                found = False
#                for day in days:
#                    if day.key().id() == appointment.day.key().id():
#                        found = True
#                        break
#                if not found:
#                    days.append(appointment.day)
#            
#            days_appointments = []
#            for day in days:
#                appointments_in_day = []
#                for appointment in appointments:
#                    if appointment.day.key().id() == day.key().id():
#                        appointments_in_day.append(appointment)
#                
#                days_appointments.append([day, appointments_in_day])
#            
#            days_tables_appointments = []
#            for day_appointments in days_appointments:
#                tables = []
#                for appointment in day_appointments[1]:
#                    if appointment.table not in tables:
#                        tables.append(int(appointment.table))
#                
#                day_tables = []
#                for table in tables:
#                    table_appointments = []
#                    for appointment in day_appointments[1]:
#                        if int(appointment.table) == table:
#                            table_appointments.append(appointment)
#                    day_tables.append([table, table_appointments])
#                days_tables_appointments.append([day_appointments[0], day_tables])
#                
#            day_tables_slots = []
#            for day_tables_appointments in days_tables_appointments:
#                for table_appointments in day_tables_appointments[1]:
#                    table_slots = []
#                    for slot in range(1, day_tables_appointments[0].talks+1):
#                        added = False
#                        for appointment in table_appointments[1]:
#                            if(int(appointment.slot) == slot):
#                                added = True
#                                table_slots.append(appointment)
#                        if not added:
#                            table_slots.append(1)
#                    day_tables_slots.append([day_tables_appointments[0], [table_appointments[0], table_slots]])
        elif method == 'teacher':
            teacher = Teacher.get_by_key_name(code.upper())
            if not teacher:
                notifications.append('Er is geen docent gevonden met de opgegeven docentcode.')
            if teacher:
                subjects = teacher.subjects.fetch(999)
                requests = []
                for subject in subjects:
                    reqs = subject.requests.fetch(999)
                    for req in reqs:
                        requests.append(req)
                appointments = [request.appointment.get() for request in requests if request.appointment.get()]
                if not appointments:
                    notifications.append("Er zijn geen afspraken gevonden voor de docent met docentcode " + str(code))
                    
        path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-appointments.html')
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
    
    @staticmethod
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

class AdministrationSendAppointmentsHandler(webapp.RequestHandler):
    
    def get(self, arg):
        event = Event.get_by_id(int(arg))
        notifications = []
        if not event:
            notifications.append("De bewerking kon niet worden voltooid omdat het event niet bestaat.")
            events = Event.all()
            path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-list.html')
            template_values = {'events': events, 'logoutlink': users.create_logout_url("/") , 'notifications': notifications }
            self.response.out.write(template.render(path, template_values))
            return
        
        requests = event.requests.fetch(9999)
        guardians_keys = []
        
        for request in requests:
            if request.guardian.key().name() not in guardians_keys:
                guardians_keys.append(request.guardian.key().name())
        
        if not guardians_keys:
            notifications.append("Er zijn geen voogden met verzoeken")
            events = Event.all()
            path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-list.html')
            template_values = {'events': events, 'logoutlink': users.create_logout_url("/") , 'notifications': notifications }
            self.response.out.write(template.render(path, template_values))
            return
            
        for guardian_num, guardian_key in enumerate(guardians_keys):
            guardian = Guardian.get_by_key_name(guardian_key)
            guardian_requests = Request.gql("WHERE guardian = :1 AND event = :2", guardian, event).fetch(999)
            guardian_appointments = [guardian_request.appointment.get() for guardian_request in guardian_requests if guardian_request.appointment.get()]
            day_ids = [appointment.day.key().id() for appointment in guardian_appointments if appointment]
            day_ids = list(set(day_ids))

            if not guardian_appointments:
                continue

            mail = Email()
            message = 'Beste ' + guardian.title
            if not guardian.preposition == '':
                message += ' ' + guardian.preposition
            message += ' ' + guardian.lastname + ',\n\n'
            message += 'Er zijn afspraken ingepland voor de ouderavond(en) van het ' + event.event_name + ". "
            message += 'Hieronder vind u de afspraken die voor u zijn gemaakt:\n\n'

            for day_id in day_ids:
                day = Day.get_by_id(day_id)
                message += 'Op ' + str(day.date.day) + ' ' + AdministrationInviteGuardiansHandler.getMonthText(self, day.date.month) + ' '  + str(day.date.year) + ':\n' 
                for appointment in guardian_appointments:
                    if appointment.day.key().id() == day_id:
                        student = appointment.request.student
                        m = event.talk_time * appointment.slot
                        d = timedelta(minutes=m)
                        time = day.date + d
                        message += 'Tijd: ' + str(time.hour) + ':' + str(time.minute) + '\n'
                        message += 'Tafel: ' + str(appointment.table) + '\n'
                        message += 'Leerling: ' + student.firstname + ' ' + student.preposition + ' ' + student.lastname + '\n'
                        message += 'Vak: ' + appointment.request.combination.subject.name + '\n'
                        message += 'Docent: ' + appointment.request.combination.teacher.name + '\n'
                        message += 'Docentcode: ' + appointment.request.combination.teacher.key().name() + '\n\n'
                    
#            mail.sendMail(guardian.email, 'Afspraken ouderavond(en) ' + event.event_name, message)
            if guardian_num == 0:
                print message
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
        
