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
from models.subscriptiondetails import SubscriptionDetails

class Subscribe(webapp.RequestHandler):
#        /inschrijven/1285/1111

    #@todo: authorization ok?
    #@todo: how do users log in?
    #@todo: where to go after good post?


    def get(self, eventId, guardianId):
        event = Event.get_by_id(int(eventId))
        days = Day.gql("WHERE event = :1", event).fetch(999)
        guardian = Guardian.get_by_key_name(guardianId)
        errors = []
        templVal = {
            'errors': errors
        }
        subscriptionDetailsList = SubscriptionDetails.gql("WHERE event = :1 AND guardian = :2", event, guardian).fetch(1, 0)
        subscriptionDetails = subscriptionDetailsList[0]
        if subscriptionDetails and subscriptionDetails.requested:
            errors.append('U kunt geen verzoeken meer indienen.')
            self.showError(templVal)
            return            
        
        students = Student.gql("WHERE guardian = :1", guardian).fetch(999, 0)
        students_subjects = self.getStudentsSubjects(students) 

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
        students_subjects = self.getStudentsSubjects(students)
        errors = []
        templVal = {
            'event': event,
            'days': days,
            'guardian': guardian,
            'students': students_subjects,
            'errors': errors
        }
           
        if not (event and days and guardian and students):
            errors.append('U probeert een onmogelijke bewerking uit te voeren.')
            self.showError(templVal)
            return
        
        subscriptionDetailsList = SubscriptionDetails.gql("WHERE event = :1 AND guardian = :2", event, guardian).fetch(1, 0)
        subscriptionDetails = subscriptionDetailsList[0]
        if subscriptionDetails and subscriptionDetails.requested:
            errors.append('U kunt geen verzoeken meer indienen.')
            self.showError(templVal)
            return
        
        studentKeys = [str(k.replace('subject_', '')) for k in self.request.arguments() if re.match("subject_.+", k)]
        requests = []
        dayPrefs = []
        
        for s in students[:]:
            if str(s.key().name()) not in studentKeys:
                students.remove(s)
                
        if not students:
            errors.append('U kunt geen verzoek indienen als u geen enkel vak geselecteerd heeft. ')
        
        for student in students[:]:
            subjectCodes = [c for c in self.request.get_all("subject_" + str(student.key().name()))]
            subjects = Subject.get_by_key_name(subjectCodes)
            if len(subjectCodes) > 3:
                errors.append('U kunt maximaal 3 vakken per leerling bespreken.')
            if len(subjectCodes) != len(subjects):
                errors.append('U probeert een onmogelijke bewerking uit te voeren.')
                
            for subject in subjects:
                combination = Combination.gql("WHERE class_id = :1 AND subject = :2", student.class_id, subject).fetch(1,0)[0]
                if not combination:
                    errors.append('U probeert een onmogelijke bewerking uit te voeren.')
                    self.showError(templVal)
                    return
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
        if not (self.request.get('time_pref') and (int(self.request.get('time_pref')) in [0,1,2])):
            errors.append('U moet een voorkeur voor tijd aangeven.')
        else:            
            timePref.preference = int(self.request.get('time_pref'))
        
        dayKeys = [long(k.replace('date_', '')) for k in self.request.arguments() if re.match("date_.+", k)]
        dayKeysFromStore= [day.key().id() for day in days]
        daysOk = True
        for dayKey in dayKeys:
            if dayKey not in dayKeysFromStore:
                daysOk = False
                errors.append('U probeert een onmogelijke bewerking uit te voeren.')
                self.showError(templVal)
                return
            
        dayPrefsList = [int(self.request.get(k)) for k in self.request.arguments() if re.match("date_.+", k)]
        dayPrefsList.sort()
        dayPrefsOk = True
        if dayPrefsList != [1,2,3]:
            dayPrefsOk = False
            errors.append('U moet een eerste, een tweede en een derde voorkeur aangeven')

        
        if daysOk and dayPrefsOk:
            for day in days:
                dayPref = DayPreference()
                dayPref.day = day
                dayPref.guardian = guardian
                dayPref.rank = int(self.request.get("date_" + str(day.key().id())))
                dayPrefs.append(dayPref)
        
        if errors:
            path = os.path.join(os.path.dirname(__file__), '../templates/subscription.html')
            self.response.out.write(template.render(path, templVal))
            return
        
        for request in requests:
            request.put()
        for dayPref in dayPrefs:
            dayPref.put()
        timePref.put()
        subscriptionDetails.requested = True
        subscriptionDetails.put()
        

    def getStudentsSubjects(self, students):
        students_subjects = []
        for student in students:
            class_id = student.class_id 
            combinations = Combination.gql("WHERE class_id = :1", class_id).fetch(10, 0)
            subjects = []
            for combination in combinations:
                subjects.append(combination.subject)
            students_subjects.append([student, subjects])
        return students_subjects

    def showError(self, templVal):
        path = os.path.join(os.path.dirname(__file__), '../templates/error.html')
        self.response.out.write(template.render(path, templVal))






class SubscriptionLoginHandler(webapp.RequestHandler):
    
    def get(self):
        session = get_current_session()
        '''A guardian is already logged in'''
        if self.isLoggedIn():
            self.redirectToSubscriptionPage()
            return
        
        '''A visitor is not authenticated as a guardian, so move on to the login page'''
        session.terminate()
        self.showLoginPage({})
        return
    
    def post(self):
        session = get_current_session()
        '''A guardian is already logged in'''
        if self.isLoggedIn():
            self.redirectToSubscriptionPage()
            return
        
        '''A visitor is not authenticated as a guardian, so move on'''
        session.clear()
        notifications = []
        templVal = {
            'notifications': notifications
        }
        
        '''The guardian-id and/or passphrase are/is empty'''
        if not (self.request.get('guardian-id') and self.request.get('passphrase')):
            notifications.append('Vul uw verzorgersnummer in en de sleutel die u ontvangen heeft.')
            self.showLoginPage(templVal)
            return

        guardian = Guardian.get_by_key_name(self.request.get('guardian-id'))
        passphrase = self.request.get('passphrase')
        
        '''A gardian with the given keyname does not exists'''
        if not guardian:
            notifications.append('Vul een bestaand verzorgersnummer in.')
            self.showLoginPage(templVal)
            return

        '''A combination of the gardian and the passphrase does not exists.'''
        subscriptionDetailsList = SubscriptionDetails.gql("WHERE guardian = :1 AND passphrase = :2", guardian, passphrase).fetch(1,0)
        if not subscriptionDetailsList:
            notifications.append('Vul een geldige combinatie van verzorgersnummer en sleutel in.')
            self.showLoginPage(templVal)
            return
        
        subscriptionDetails = subscriptionDetailsList[0]
        
        '''The guardian has already made a subscription for the concerning event'''
        if subscriptionDetails.requested:
            notifications.append('U heeft al een inschrijving gedaan.')
            #@TODO
            return
        
        '''Everything is ok, so login and go to the subscription page!'''
        event = subscriptionDetails.event
        session['guardian'] = guardian
        session['event'] = event
        self.redirectToSubscriptionPage()

    def isLoggedIn(self):
        session = get_current_session()
        if session.is_active():
            if session['guardian'] and session['event']:
                return True
        return False

    def redirectToSubscriptionPage(self):
        session = get_current_session()
        event = session['event']
        guardian = session['guardian']
        self.redirect('/inschrijven/'+ str(event.key().id()) + '/' + str(guardian.key().name()))
    
    def showLoginPage(self, templVal={}):
        path = os.path.join(os.path.dirname(__file__), '../templates/subscription/subscription-login.html')
        self.response.out.write(template.render(path, templVal))
        

class SubscriptionLogoutHandler(webapp.RequestHandler):
    
    def get(self):
        session = get_current_session()
        session.terminate()
        self.showLogoutPage()

    def showLogoutPage(self):
        path = os.path.join(os.path.dirname(__file__), '../templates/subscription/subscription-logout.html')
        self.response.out.write(template.render(path, {}))

