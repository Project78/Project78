'''
Created on Dec 18, 2011

@author: averaart
'''

from google.appengine.ext import webapp
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
from classes.planning import Planning


class plan(webapp.RequestHandler):
    def get(self):
        event = Event.all().filter("event_name", "paasrapport").get()
        days = Day.all().filter("event", event).fetch(999)
        days.sort(key=lambda day: day.date)
        max_requests = 0
        max_timepref = 0
        max_rank = 0
        allguardians = Guardian.all().fetch(10)
        guardians = []
        requests = []
        for guardian in allguardians:
            requests = Request.all().filter("guardian", guardian).filter("event", event).fetch(999)
            if len(requests) > 0:
                max_requests = max([max_requests, len(requests)])
                guardian.requests = requests
                guardian.day_prefs = []
                for day in days:
                    guardian.day_prefs.append(DayPreference.all().filter("guardian", guardian).filter("day", day).get())
                guardian.day_prefs.sort(key=lambda day: day.rank)
                max_rank = max([max_rank, max([day.rank for day in guardian.day_prefs])])
                guardian.time_pref = TimePreference.all().filter("guardian", guardian).filter("event", event).get()
                max_timepref = max([max_timepref, guardian.time_pref.preference])
                guardians.append(guardian)

        timepref_options = range(max_timepref+1)
        print ""
        timepref_options = [1,2,0]
        
        planning = Planning(event, days)
        
#        for i, day in enumerate(planning.days):
#            print "Day: "+(str)(i+1)
#            for table in day:
#                text = ""
#                for slot in table:
#                    if slot is None:
#                        text += "0 "
#                    else:
#                        text += "1 "
#                print text
        
        day = planning.days[0]
        day[0][0]=1
        day[0][1]=1
        day[0][2]=1
        day[1][0]=1
        day[1][1]=1
        day[2][0]=1
        day[2][1]=1
        day[2][2]=1
        day[2][3]=1
        day[4][0]=1
        
        print [table.index(None) for table in day]
        
        for timepref in timepref_options:
            print "Guardians with timepref: "+str(timepref)
            for length in range (max_requests, 0, -1):
                print "Guardians with "+str(length)+" requests:"
                for rank in range(1, max_rank+2):
                    print "With day as rank: "+str(rank)
                    for day in days:
                        for guardian in filter(lambda guardian: (len(guardian.requests) == length)
                                           and (guardian.time_pref.preference == timepref) 
                                           and (filter(lambda day_pref: day_pref.day.date == day.date, guardian.day_prefs)[0].rank == rank),
                                           guardians):
                            print guardian.title +" "+ guardian.lastname +" wil op "+day.date.strftime("%d-%m-%y")+" praten met:"
                            for request in guardian.requests:
                                print "    "+request.combination.teacher.name +" over "+ request.combination.subject.name
                                

        
                
                

#        for length in range (max_requests, 0, -1):
#            print "Guardians with "+str(length)+" requests:"
#            for day in days:
#                print day.date.strftime("%d-%m-%y")
#                for guardian in filter(lambda guardian: (len(guardian.requests) == length)
#                                   and (filter(lambda day_pref: day_pref.day.date == day.date, guardian.day_prefs)[0].rank == 1),
#                                   guardians):
#                    print guardian.lastname