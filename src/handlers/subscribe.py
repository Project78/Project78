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
from gaesessions import get_current_session

class SubscriptionHandler(webapp.RequestHandler):

    def get(self, eventId, guardianId):
        '''The visitor is not an authenticated guardian'''
        if not SubscriptionLoginHandler.isAuthenticatedGuardian():
            self.redirect('/inschrijven/')
            return
        
        '''The guardian is not authorized to see the page with the given eventId/guardianId'''
        if not self.isAuthorized(eventId, guardianId):
            SubscriptionLoginHandler.redirectToSubscriptionPage(self)
            return
        
        '''The guardian is an authorized guardian, so show the form'''    
        event = Event.get_by_id(int(eventId))
        days = Day.gql("WHERE event = :1", event).fetch(999)
        guardian = Guardian.get_by_key_name(guardianId)
        notifications = []
        templVal = {
            'notifications': notifications
        }
        subscriptionDetailsList = SubscriptionDetails.gql("WHERE event = :1 AND guardian = :2", event, guardian).fetch(1, 0)
        if not subscriptionDetailsList:
            notifications.append('Pagina niet gevonden.')
            self.showError(templVal)
            return    
        subscriptionDetails = subscriptionDetailsList[0]
        if subscriptionDetails and subscriptionDetails.requested:
            notifications.append('U kunt geen verzoeken meer indienen.')
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
            path = os.path.join(os.path.dirname(__file__), '../templates/subscription/subscription.html')
            self.response.out.write(template.render(path, templVal))
        
        
    def post(self, eventId, guardianId):
        '''The visitor is not an authenticated guardian'''
        if not SubscriptionLoginHandler.isAuthenticatedGuardian():
            self.redirect('/inschrijven/')
            return
        
        '''The guardian is not authorized to the given'''
        if not self.isAuthorized(eventId, guardianId):
            SubscriptionLoginHandler.redirectToSubscriptionPage(self)
            return
        
        event = Event.get_by_id(int(eventId))
        days = Day.gql("WHERE event = :1", event).fetch(999)
        guardian = Guardian.get_by_key_name(guardianId)
        students = Student.gql("WHERE guardian = :1", guardian).fetch(999, 0)
        students_subjects = self.getStudentsSubjects(students)
        notifications = []
        templVal = {
            'event': event,
            'days': days,
            'guardian': guardian,
            'students': students_subjects,
            'notifications': notifications
        }
           
        if not (event and days and guardian and students):
            notifications.append('U probeert een onmogelijke bewerking uit te voeren.')
            self.showError(templVal)
            return
        
        subscriptionDetailsList = SubscriptionDetails.gql("WHERE event = :1 AND guardian = :2", event, guardian).fetch(1, 0)
        if not subscriptionDetailsList:
            notifications.append('Pagina niet gevonden.')
            self.showError(templVal)
            return           
        subscriptionDetails = subscriptionDetailsList[0]
        if subscriptionDetails and subscriptionDetails.requested:
            notifications.append('U kunt geen verzoeken meer indienen.')
            self.showError(templVal)
            return
        
        studentKeys = [str(k.replace('subject_', '')) for k in self.request.arguments() if re.match("subject_.+", k)]
        requests = []
        dayPrefs = []
        
        for s in students[:]:
            if str(s.key().name()) not in studentKeys:
                students.remove(s)
                
        if not students:
            notifications.append('U kunt geen verzoek indienen als u geen enkel vak geselecteerd heeft. ')
        
        for student in students[:]:
            subjectCodes = [c for c in self.request.get_all("subject_" + str(student.key().name()))]
            subjects = Subject.get_by_key_name(subjectCodes)
            if len(subjectCodes) > 3:
                notifications.append('U kunt maximaal 3 vakken per leerling bespreken.')
            if len(subjectCodes) != len(subjects):
                notifications.append('U probeert een onmogelijke bewerking uit te voeren.')
                
            for subject in subjects:
                combination = Combination.gql("WHERE class_id = :1 AND subject = :2", student.class_id, subject).fetch(1,0)[0]
                if not combination:
                    notifications.append('U probeert een onmogelijke bewerking uit te voeren.')
                    self.showError(templVal)
                    return
                request = Request()
                request.event = event
                request.guardian = guardian
                request.student = student
                request.combination = combination
                requests.append(request)

        '''Process timepreference'''
        timePref = TimePreference()
        timePref.event = event
        timePref.guardian = guardian
        timePref.preference = 0
        if not (self.request.get('time_pref') and (int(self.request.get('time_pref')) in [0,1,2])):
            notifications.append('U moet een voorkeur voor tijd aangeven.')
        else:            
            timePref.preference = int(self.request.get('time_pref'))
        
        '''Check if dates from the form match the dates from the event '''
        dayKeys = [long(k.replace('date_', '')) for k in self.request.arguments() if re.match("date_.+", k)]
        dayKeysFromStore= [day.key().id() for day in days]
        daysOk = True
        for dayKey in dayKeys:
            if dayKey not in dayKeysFromStore:
                daysOk = False
                notifications.append('U probeert een onmogelijke bewerking uit te voeren.')
                self.showError(templVal)
                return

        '''Check if the daypreference are correct filled in'''    
        dayPrefsList = [int(self.request.get(k)) for k in self.request.arguments() if re.match("date_.+", k)]
        dayPrefsList.sort()
        dayPrefsOk = True
        if dayPrefsList != [1,2,3]:
            dayPrefsOk = False
            notifications.append('U moet een eerste, een tweede en een derde voorkeur aangeven')

        '''Process daypreferences'''
        if daysOk and dayPrefsOk:
            for day in days:
                dayPref = DayPreference()
                dayPref.day = day
                dayPref.guardian = guardian
                dayPref.rank = int(self.request.get("date_" + str(day.key().id())))
                dayPrefs.append(dayPref)
        
        if notifications:
            path = os.path.join(os.path.dirname(__file__), '../templates/subscription/subscription.html')
            self.response.out.write(template.render(path, templVal))
            return
        
        '''Store the requests'''
        for request in requests:
            request.put()
        for dayPref in dayPrefs:
            dayPref.put()
        timePref.put()
        subscriptionDetails.requested = True
        subscriptionDetails.put()
        
        SubscriptionLogoutHandler.logoutGuardian()
        path = os.path.join(os.path.dirname(__file__), '../templates/subscription/subscription-success.html')
        self.response.out.write(template.render(path, templVal))
        return        
    
    '''Is the guardian trying to subscribe for itself'''
    def isAuthorized(self, eventId, guardianId):
        session = get_current_session()
        event = session['event']
        guardian = session['guardian']
        if not (int(eventId) == int(event.key().id()) and int(guardianId) == int(guardian.key().name())):
            return False
        return True
    
    '''Returns an array containing arrays with combinations of students and the subjects they follow'''
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

    ''''Show the notification page'''
    def showError(self, templVal):
        path = os.path.join(os.path.dirname(__file__), '../templates/notification.html')
        self.response.out.write(template.render(path, templVal))

class SubscriptionLoginHandler(webapp.RequestHandler):
    
    def get(self):
        session = get_current_session()
        '''A guardian is already logged in'''
        if self.isAuthenticatedGuardian():
            self.redirectToSubscriptionPage(self)
            return
        
        '''A visitor is not authenticated as a guardian, so move on to the login page'''
        session.terminate()
        self.showLoginPage({})
        return
    
    def post(self):
        session = get_current_session()
        '''A guardian is already logged in'''
        if self.isAuthenticatedGuardian():
            self.redirectToSubscriptionPage(self)
            return
        
        '''A visitor is not authenticated as a guardian, so move on'''
        session.clear()
        notifications = []
        templVal = {
            'notifications': notifications
        }
        
        '''The guardian-id and/or passphrase are/is empty'''
        if not (self.request.get('guardian-id') and self.request.get('passphrase')):
            notifications.append('Vul uw voogdnummer in en de sleutel die u ontvangen heeft.')
            self.showLoginPage(templVal)
            return

        guardian = Guardian.get_by_key_name(self.request.get('guardian-id'))
        passphrase = self.request.get('passphrase')
        
        '''A gardian with the given keyname does not exists'''
        if not guardian:
            notifications.append('Vul een bestaand voogdnummer in.')
            self.showLoginPage(templVal)
            return

        '''A combination of the gardian and the passphrase does not exists.'''
        subscriptionDetailsList = SubscriptionDetails.gql("WHERE guardian = :1 AND passphrase = :2", guardian, passphrase).fetch(1,0)
        if not subscriptionDetailsList:
            notifications.append('Vul een geldige combinatie van voogdnummer en sleutel in.')
            self.showLoginPage(templVal)
            return
        
        subscriptionDetails = subscriptionDetailsList[0]
        
        '''The guardian has already made a subscription for the concerning event'''
        if subscriptionDetails.requested:
            notifications.append('U kunt geen verzoeken meer indienen.')
            path = os.path.join(os.path.dirname(__file__), '../templates/notification.html')
            self.response.out.write(template.render(path, templVal))
            return
        
        '''Everything is ok, so login and go to the subscription page!'''
        event = subscriptionDetails.event
        session['guardian'] = guardian
        session['event'] = event
        self.redirectToSubscriptionPage(self)

    @staticmethod
    def isAuthenticatedGuardian():
        session = get_current_session()
        if session.is_active():
            if session['guardian'] and session['event']:
                return True
        return False

    @staticmethod
    def redirectToSubscriptionPage(r):
        session = get_current_session()
        event = session['event']
        guardian = session['guardian']
        r.redirect('/inschrijven/'+ str(event.key().id()) + '/' + str(guardian.key().name()))
    
    def showLoginPage(self, templVal={}):
        path = os.path.join(os.path.dirname(__file__), '../templates/subscription/subscription-login.html')
        self.response.out.write(template.render(path, templVal))
        
class SubscriptionLogoutHandler(webapp.RequestHandler):
    
    def get(self):
        self.logoutGuardian()
        self.redirect('/inschrijven/')
    
    @staticmethod    
    def logoutGuardian():
        session = get_current_session()
        session.terminate()