'''
Created on Dec 18, 2011

@author: averaart
'''

import time
import random
import math

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
        
        print ""
        print "<html><body style='font-family: Helvetica; font-size: 0.9em;'>"
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
               
                
        for dayIndex, day in enumerate(planning.days):
            safety = 0                                                      # <--- general infinite loop preventer
            slotNum = 0
            consecutiveCleanUps = 0
            direction = 1
            
            # Perform until all slots have been cleaned in one go
            while consecutiveCleanUps < len(planning.flipped(day)):
                print "Working on slot index: "+str(slotNum) +"<br>"
                print "consecutiveCleanUps: " + str(consecutiveCleanUps) +"<br>"
                print "direction: "+str(direction) +"<br>"
                print  "<br>"
                
                conflictSafety = 0                                          # <--- slot infinite loop preventer
                slot = planning.flipped(day)[slotNum]
                conflicted = planning.conflictedTeachers(day, slotNum)

                while(conflicted):
                    teachers = map(planning.getTeacherStringFromRequest, planning.flipped(day)[slotNum])
                    moveCounters = map(planning.getMoveCounter, planning.flipped(day)[slotNum])

                    # all indices with the conflicted teacher
                    indices = [j for j, x in enumerate(teachers) if x == conflicted[0]]
                    
                    # find occurrences of teacher closest to startingPosition
                    allStartingPositions = map(planning.getStartingPosition, slot)
                    
                    teacherDistances = []
                    for index in indices:
                        teacherDistances.append(slotNum-allStartingPositions[index])
                                            
                    if direction > 0:
                        mostFavorableDistance = min(teacherDistances)
                    else:
                        mostFavorableDistance = max(teacherDistances)
                    
                    smallestDistanceIndices = [index for enum, index in enumerate(indices) if teacherDistances[enum] == mostFavorableDistance]
                    
                    # search for the occurrence of teacher with lowest moveCounter
                    teacherMoveCounters = [moveCounters[x] for x in smallestDistanceIndices]
                    lowestMoveCounter = min(teacherMoveCounters)
                    lowestMoveCounterIndex = teacherMoveCounters.index(lowestMoveCounter)
                    index = indices[lowestMoveCounterIndex]
                    
                    # If the end is reached and there are still conflicts, start moving backwards
                    if slotNum >= len(planning.flipped(day))-1:
                        direction = -1
                        consecutiveCleanUps = 0
                        print "I'm working on slot index "+str(slotNum)+" and I've set direction to "+str(direction) +"<br>"
                    # If the start is reached and there are still conflicts, start moving forwards    
                    if slotNum <= 0:
                        direction = 1
                        consecutiveCleanUps = 0
                        print "I'm working on slot index "+str(slotNum)+" and I've set direction to "+str(direction) +"<br>"
                      
                    day[index][slotNum], day[index][slotNum+direction] = day[index][slotNum+direction], day[index][slotNum]
                    if day[index][slotNum] != None:
                        day[index][slotNum].moveCounter += 1
                    if day[index][slotNum+direction] != None:
                        day[index][slotNum+direction].moveCounter += 1
                    
                    conflicted = planning.conflictedTeachers(day, slotNum)
                    conflictSafety += 1
                    
                    # If solving takes too long, approach from the other direction
                    if conflictSafety > 25:
                        slotNum = random.randrange(-1, len(planning.flipped(day)))
                        if slotNum < 0:
                            slotNum = 0
#                        if slotNum == 0:
#                            direction = 1
#                        elif slotNum == (len(planning.flipped(day))-1):
#                            direction = -1
#                        else:
#                            direction *= -1
                        
                        consecutiveCleanUps = -1
                        print "Conflict list seems to be hanging. Switching!<br>"
                        conflictSafety = 0
                        break
                
                # <--- End of while(conflicted) loop
                
                
                consecutiveCleanUps += 1 
                slotNum+=direction
                if slotNum >= len(planning.flipped(day)):
                    slotNum = len(planning.flipped(day))-1
                    direction = -1
                    consecutiveCleanUps = 0
                    print "consecutiveCleanUps set to zero at line 202<br>"
                if slotNum < 0:
                    slotNum = 0
                    direction = 1
                    consecutiveCleanUps = 0
                    print "consecutiveCleanUps set to zero at line 207<br>"
                safety +=1
                if safety > 1000:
                    print "LOOP?!?<br>"
                    break
                
            # <--- End of while consecutiveCleanUps < len(planning.flipped(day)) loop 
            

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