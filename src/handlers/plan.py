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
        allguardians = Guardian.all().fetch(9999)
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
            
        for length in range (max_requests, 0, -1):
            for timepref in timepref_options:
                for rank in range(0, max_rank+1):
                    for day_num, day in enumerate(days):
                        for guardian in filter(lambda guardian: (len(guardian.requests) == length)
                                           and (guardian.time_pref.preference == timepref) 
                                           and (filter(lambda day_pref: day_pref.day.date == day.date, guardian.day_prefs)[0].rank == rank),
                                           guardians):
                            # print "timepref: " + str(timepref) + " - length: " + str(length) + " - day_num: " + str(day_num) + " - ranked: " + str(rank) + " guardian: "+guardian.title +" "+ guardian.lastname
                            # print guardian.title +" "+ guardian.lastname +" wil op "+day.date.strftime("%d-%m-%y")+" praten over " + str(len(guardian.requests)) + " vakken"
                                
                            # try to place these requests     
                            placed = planning.place(guardian, day_num)
                            
                            # on succes, remove guardian from guardian
                            # on fail, the guardian will return on a less preferable round
                            if (placed):
                                guardians.remove(guardian)

#        planning.pprint()
#        planning.days[0][0][1], planning.days[0][0][3] = planning.days[0][0][3], planning.days[0][0][1]
#        planning.pprint()
        
        for dayIndex, day in enumerate(planning.days):
            i = 0
            direction = 1
            while 0 <= i < len(planning.flipped(day)):
                slot = planning.flipped(day)[i]
                conflicted = planning.conflictedTeachers(day, i)
                while(conflicted):
#                    print conflicted
                    teachers = map(planning.getTeacherStringFromRequest, planning.flipped(day)[i])
                    moveCounters = map(planning.getMoveCounter, planning.flipped(day)[i])
                    # all indices with the conflicted teacher
                    indices = [j for j, x in enumerate(teachers) if x == conflicted[0]]
                    teacherMoveCounters = [moveCounters[x] for x in indices]
                    lowestMoveCounter = min(teacherMoveCounters)
                    lowestMoveCounterIndex = teacherMoveCounters.index(lowestMoveCounter)
                    index = indices[lowestMoveCounterIndex]
                    if i == len(planning.flipped(day))-1:
                        direction = -1
                        
#                    print "all teachers in slot "+str(i)+": "+str(teachers)
#                    print "respective moveCounters: "+str(moveCounters)
#                    print "conflicted teacher: " +str(conflicted[0])
#                    print "indices of the current conflicted teacher: "+ str(indices)
#                    print "moveCounters for current conflicted teacher: "+str(teacherMoveCounters)
#                    print "lowest moveCounter for current conflicted teacher: "+str(lowestMoveCounter)
#                    print "table position of conflicted teacher in slot: "+str(index)
                                            
                    day[index][i], day[index][i+direction] = day[index][i+direction], day[index][i]
                    if day[index][i] != None:
                        day[index][i].moveCounter += 1
                    if day[index][i+direction] != None:
                        day[index][i+direction].moveCounter += 1
#                    print "Day: "+str(dayIndex+1)
#                    planning.pprint_day(day)
                    conflicted = planning.conflictedTeachers(day, i)

                i+=direction
                        
        planning.outputHTML()
        
#        myDay = []
#        
#        for table in planning.days[2]:
#            for slot in table:
#                myDay.append(planning.getTeacherStringFromRequest(slot))
#            
#        print myDay
#        
#        mySet = set(myDay)
#        myList = list(mySet)
#        
#        for teacher in myList:
#            print myDay.count(teacher)


        
#        for length in range (max_requests, 0, -1):
#            print "Guardians with "+str(length)+" requests:"
#            for day in days:
#                print day.date.strftime("%d-%m-%y")
#                for guardian in filter(lambda guardian: (len(guardian.requests) == length)
#                                   and (filter(lambda day_pref: day_pref.day.date == day.date, guardian.day_prefs)[0].rank == 1),
#                                   guardians):
#                    print guardian.lastname