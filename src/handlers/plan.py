'''
Created on Dec 18, 2011

@author: averaart
'''

import time
import random
import math
import itertools

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
from models.Appointment import Appointment
from classes.planning import Planning


class plan(webapp.RequestHandler):
    def get(self, arg):
        
        print ""
        print "<html><body style='font-family: Helvetica; font-size: 0.9em;'>"
        print time.strftime("%H:%M:%S", time.localtime())+": Start<br>"
        
        if arg != None:
            event = Event.get_by_id(int(arg))
        else:
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
        
        print time.strftime("%H:%M:%S", time.localtime())+": All guardians/requests collected<br>"
        
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
               
        print time.strftime("%H:%M:%S", time.localtime())+": Placed<br>"

        planning.outputHTML()        

        for day in planning.days:
            
            conflicts = 0
            for i, slot in enumerate(day[0]):
                conflicts += len(planning.conflictedTeachers(day, i))
            print time.strftime("%H:%M:%S", time.localtime())+": "+str(conflicts)+"<br>"
            
            # <--- Build a list of all regions
        
            regions = []
            for tableIndex, table in enumerate(day):

                region = [tableIndex, 0, -1]
                previousGuardian = ""

                for slotIndex, slot in enumerate(table):

                    guardianId = planning.getGuardianIdFromRequest(slot)
                    block = table[region[1]:region[2]+1]
                    
                    if guardianId == "":
                        if len(block) == 0:
                            region = [tableIndex, slotIndex, slotIndex]
                        elif block.count(None) == 0:
                            if previousGuardian != "":
                                region[2] = slotIndex
                                regions.append(region)
                                region = [tableIndex, 0, -1]
                        elif block.count(None) > 0:
                            regions.append(region)
                            region = [tableIndex, slotIndex, slotIndex]
                        previousGuardian = ""
                    else:
                        if guardianId != previousGuardian and previousGuardian != "":
                            regions.append(region)
                            region = [tableIndex, slotIndex, slotIndex]
                        region[2] = slotIndex
                        previousGuardian = guardianId
                                
                block = table[region[1]:region[2]+1]
                if len(block) > 0:
                    regions.append(region)

            
            # <--- Find all permutations
            
            permutationSets = []
            
            for set in regions:          
                block = day[set[0]][set[1]:set[2]+1]
                permutations = itertools.permutations(block)
                permutations = list(permutations)
                permutationSets.append(permutations)
            
            
     
            # <---- Op basis van willekeurige permutaties 
           
            for loop in range(1):
                    
                for setIndex, set in enumerate(regions):          
                    conflictCounter = []
                    
                    for perm in permutationSets[setIndex]:
                        
                        block = day[set[0]][set[1]:(set[2]+1)]
                        day[set[0]][set[1]:(set[2]+1)] = perm
                        
                        conflicts = 0                    
                        for i, slot in enumerate(day[0]):
                            conflicts += len(planning.conflictedTeachers(day, i))
                        conflictCounter.append(conflicts)
                    
                    lowestValue = min(conflictCounter)
                    
                    bestOptions = [enum for enum, x in enumerate(conflictCounter) if x == lowestValue]
                    bestOption = random.choice(bestOptions)
                    newList = permutationSets[setIndex][bestOption]
                    day[set[0]][set[1]:set[2]+1] = newList
                   
                conflicts = 0
                for i, slot in enumerate(day[0]):
                    conflicts += len(planning.conflictedTeachers(day, i))
                print time.strftime("%H:%M:%S", time.localtime())+": "+str(conflicts)+"<br>"




        planning.outputHTML()
        
        for dayIndex, day in enumerate(planning.days):
            for tableIndex, table in enumerate(day):
                for slotIndex, slot in enumerate(table):
                    if slot != None:
                        new_appointment = Appointment(request=slot,
                                                      day=days[dayIndex],
                                                      table=tableIndex,
                                                      slot=slotIndex)
                        new_appointment.put()
