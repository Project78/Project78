'''
Created on Dec 18, 2011

@author: averaart
'''

import time
import random

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
        
#        print ""
#        print time.strftime("%H:%M:%S", time.localtime())+": Start"
        
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
        timepref_options = [1,2,0]
        
        planning = Planning(event, days)
        
#        print time.strftime("%H:%M:%S", time.localtime())+": All guardians/requests collected"
        
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
               
#        print time.strftime("%H:%M:%S", time.localtime())+": Schedule filled without regard for feasibility"
                         
#        planning.pprint_day(planning.days[0])

        
        
        for dayIndex, day in enumerate([planning.days[0]]):
            safety = 0                                                      # general infinite loop preventer
            slotNum = 0
            consecutiveCleanUps = 0
#            print "consecutiveCleanUps set to zero at line 89"
            direction = 1
            
            # Perform until all slots have been cleaned in one go
            while consecutiveCleanUps < len(planning.flipped(day)):
                
                conflictSafety = 0                                          # slot infinite loop preventer
                slot = planning.flipped(day)[slotNum]
                conflicted = planning.conflictedTeachers(day, slotNum)
                while(conflicted):
#                    print conflicted
                    teachers = map(planning.getTeacherStringFromRequest, planning.flipped(day)[slotNum])
                    moveCounters = map(planning.getMoveCounter, planning.flipped(day)[slotNum])
                    # all indices with the conflicted teacher
                    indices = [j for j, x in enumerate(teachers) if x == conflicted[0]]
                    teacherMoveCounters = [moveCounters[x] for x in indices]
                    lowestMoveCounter = min(teacherMoveCounters)
                    lowestMoveCounterIndex = teacherMoveCounters.index(lowestMoveCounter)
                    index = indices[lowestMoveCounterIndex]
                    
                    # If the end is reached and there are still conflicts, start moving backwards
                    if slotNum == len(planning.flipped(day))-1:
                        direction = -1
                        consecutiveCleanUps = 0
#                        print "consecutiveCleanUps set to zero at line 112"
                    # If the start is reached and there are still conflicts, start moving forwards    
                    if slotNum == 0:
                        direction = 1
                        consecutiveCleanUps = 0
#                        print "consecutiveCleanUps set to zero at line 117"
                      
#                    print "all teachers in slot "+str(slotNum)+": "+str(teachers)
#                    print "respective moveCounters: "+str(moveCounters)
#                    print "conflicted teacher: " +str(conflicted[0])
#                    print "indices of the current conflicted teacher: "+ str(indices)
#                    print "moveCounters for current conflicted teacher: "+str(teacherMoveCounters)
#                    print "lowest moveCounter for current conflicted teacher: "+str(lowestMoveCounter)
#                    print "table position of conflicted teacher in slot: "+str(index)
                                            
                    day[index][slotNum], day[index][slotNum+direction] = day[index][slotNum+direction], day[index][slotNum]
                    if day[index][slotNum] != None:
                        day[index][slotNum].moveCounter += 1
                    if day[index][slotNum+direction] != None:
                        day[index][slotNum+direction].moveCounter += 1
                    
                    conflicted = planning.conflictedTeachers(day, slotNum)
                    
                    safety += 1
                    if safety > 2500:
#                        print "Broke during a slot"
                        break
                    
                    conflictSafety += 1
                    
                    # If solving takes too long, approach from the other direction
                    if conflictSafety > 500:
                        print time.strftime("%H:%M:%S", time.localtime())+": Slot "+str(slotNum+1)+" is locking up; changing direction: "
                        if direction == 1:
                            direction = -1
                            slotNum = random.randrange(slotNum+1, len(planning.flipped(day))+1)
                        else:
                            direction = 1
                            slotNum = random.randrange(-1, slotNum)
                        consecutiveCleanUps = -1
#                        print "consecutiveCleanUps set to minus one at line 152"
                        conflictSafety = -1
                        break

#                print ""
#                print "Day: "+str(dayIndex+1)
#                planning.pprint_day(day)
#                print ""
#                if slotNum == -1 or slotNum == len(planning.flipped(day)):
#                    print ""
#                else:
#                    print time.strftime("%H:%M:%S", time.localtime())+": Slot "+str(slotNum+1)+" has been cleaned up"
                consecutiveCleanUps += 1 
                slotNum+=direction
#                if slotNum >= len(planning.flipped(day)):
#                    slotNum = len(planning.flipped(day))-1
#                    consecutiveCleanUps = 0
#                    print "consecutiveCleanUps set to zero at line 169"
#                if slotNum < 0:
#                    slotNum = 0
#                    consecutiveCleanUps = 0
#                    print "consecutiveCleanUps set to zero at line 173"
                safety +=1
                if safety > 10000:
#                    print "Broke after a slot finished"
                    break
#                print "safety: "+str(safety)
#                print "consecutiveCleanUps: "+str(consecutiveCleanUps)
                
                       
        planning.outputHTML()

        
#        for day in planning.days:
#            myDay = []
#            
#            for table in day:
#                for slot in table:
#                    myDay.append(planning.getTeacherStringFromRequest(slot))
#                
##            print myDay
#            
#            mySet = set(myDay)
#            myList = list(mySet)
#            
#            print myList
#            for teacher in myList:
#                print myDay.count(teacher)
#            print ""


        
#        for length in range (max_requests, 0, -1):
#            print "Guardians with "+str(length)+" requests:"
#            for day in days:
#                print day.date.strftime("%d-%m-%y")
#                for guardian in filter(lambda guardian: (len(guardian.requests) == length)
#                                   and (filter(lambda day_pref: day_pref.day.date == day.date, guardian.day_prefs)[0].rank == 1),
#                                   guardians):
#                    print guardian.lastname