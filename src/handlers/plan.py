'''
Created on Dec 18, 2011

@author: averaart
'''

import time
import random
import math
import itertools
import logging
import copy

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
#    def get(self, arg):
    def get(self):
        
        print ""
        print "<html><body style='font-family: Helvetica; font-size: 0.9em;'>"
        print time.strftime("%H:%M:%S", time.localtime())+": Start<br>"
        
        logging.info("Fetching all info")
        
#        if arg != None:
#            event = Event.get_by_id(int(arg))
#        else:
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
                if len(requests) > 5:
                    guardianCopy = copy.deepcopy(guardian)
                    guardian.requests = guardian.requests[:int(len(requests)/2)]
                    guardianCopy.requests = guardianCopy.requests[int(len(requests)/2):]
                    guardianCopy.day_prefs[0].rank = 999
                    guardians.append(guardianCopy)
                guardians.append(guardian)

        timepref_options = range(max_timepref+1)
        timepref_options = [1,2,0]
        
        planning = Planning(event, days)
        
        logging.info("All guardians/requests collected")
        
        for length in range (max_requests, 0, -1):
            for timepref in timepref_options:
                for rank in range(0, max_rank+1):
                    for day_num, day in enumerate(days):
                        for guardian in filter(lambda guardian: (len(guardian.requests) == length)
                                           and (guardian.time_pref.preference == timepref) 
                                           and (filter(lambda day_pref: day_pref.day.date == day.date, guardian.day_prefs)[0].rank == rank),
                                           guardians):
                                
                            # try to place these requests     
                            placed = planning.place(guardian, day_num)
                            
                            # on succes, remove guardian from guardian
                            # on fail, the guardian will return on a less preferable round
                            if (placed):
                                guardians.remove(guardian)
               
        logging.info("Placed")    

        for dayIndex, day in enumerate(planning.days):
            
            start = time.clock()
            
            lowestValue = 0
            for i, slot in enumerate(day[0]):
                lowestValue += len(planning.conflictedTeachers(day, i))
            logging.info("conflicts: "+str(lowestValue))
            
            # <--- Build a list of all regions
        
            logging.info("Building regions")
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
                            if len(block) > block.count(None):
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
                if len(block) > block.count(None) > 0:
                    regions.append(region)

            logging.info("Regions built")
            
            permutationSets = {}
            
            
            preconflicts = 0
            pre_max_conflicts = 0                    
            for i, slot in enumerate(day[0]):
                slotConflicts = len(planning.conflictedTeachers(day, i))
                pre_max_conflicts = max([pre_max_conflicts, slotConflicts])
                preconflicts += slotConflicts
            logging.info("Starting conflicts: "+str(preconflicts))
            logging.info("Starting max slotconflicts: "+str(pre_max_conflicts))
            
            for set in regions:
                block = day[set[0]][set[1]:set[2]+1]
                block.sort(key=lambda x: planning.getTeacherStringFromRequest(x))
                day[set[0]][set[1]:(set[2]+1)] = block

            sortedconflicts = 0
            sorted_max_conflicts = 0
            for i, slot in enumerate(day[0]):
                slotConflicts = len(planning.conflictedTeachers(day, i))
                sorted_max_conflicts = max([sorted_max_conflicts, slotConflicts])
                sortedconflicts += slotConflicts
            logging.info("Conflicts after sorting: "+str(sortedconflicts))
            logging.info("Max slotconflicts after sorting: "+str(sorted_max_conflicts))
            
            conflicts = 9999
            max_conflicts = 9999
            while conflicts >= preconflicts and conflicts >= sortedconflicts and max_conflicts >= pre_max_conflicts and max_conflicts >= sorted_max_conflicts:
                for set in regions:
                    block = day[set[0]][set[1]:set[2]+1]
                    random.shuffle(block)
                    day[set[0]][set[1]:(set[2]+1)] = block
    
                conflicts = 0
                max_conflicts = 0                    
                for i, slot in enumerate(day[0]):
                    slotConflicts = len(planning.conflictedTeachers(day, i))
                    max_conflicts = max([max_conflicts, slotConflicts])
                    conflicts += slotConflicts
                logging.info("Conflicts after shuffling: "+str(conflicts))
                logging.info("Max slotconflicts after shuffling: "+str(max_conflicts))
        
            # <--- Cycle through conflicted regions
            
            loop = 0
            while lowestValue > 0:

                
                logging.info("Dropping non-conflicted regions")
                conflictedRegions = [region for region in regions if planning.numberOfConflictsPerRegion(day, region) > 0 and (region[2]-region[1])<7]
                logging.info("Sorting regions to start with smallest region with highest number of conflicts")
                conflictedRegions.sort(key=lambda set: (set[2]-set[1], -planning.numberOfConflictsPerRegion(day, set)))
                            
                logging.info(str(conflictedRegions))
                
                loop+=2
                if loop > len(conflictedRegions):
                    loop = len(conflictedRegions)
                
                for set in conflictedRegions[:loop]:
                    
                    logging.info("Working on set: "+str(set))
                    logging.info("Set size: "+str(set[2]-set[1]+1))
#                    logging.info("Number of conflicts in region: "+str(planning.numberOfConflictsPerRegion(day, set)))
                    if planning.numberOfConflictsPerRegion(day, set) <= 0:
                        logging.info("Already fixed; moving on...")
                        continue
                    
                    if not tuple(set) in permutationSets:
#                        logging.info("This set is new to the dictionary")
                        block = day[set[0]][set[1]:set[2]+1]
                        permutations = itertools.permutations(block)
                        permutations = list(permutations)
                        permutationSets[tuple(set)] = permutations
                    else:
#                        logging.info("This set was already in the dictionary")
                        permutations = permutationSets[tuple(set)]
                    
                    conflictCounter = []
                                          
                    for permIndex, perm in enumerate(permutations):
                        block = day[set[0]][set[1]:(set[2]+1)]
                        day[set[0]][set[1]:(set[2]+1)] = perm
                        
                        conflicts = 0                    
                        for i, slot in enumerate(day[0]):
                            conflicts += len(planning.conflictedTeachers(day, i))
                        conflictCounter.append(conflicts)
                    
                    lowestValue = min(conflictCounter)
                    
                    bestOptions = [enum for enum, x in enumerate(conflictCounter) if x == lowestValue]
                    bestOption = random.choice(bestOptions)
                    newList = permutations[bestOption]
                    day[set[0]][set[1]:set[2]+1] = newList
                    
                    logging.info("Total conflicts: "+str(lowestValue))
                    
                    if lowestValue == 0:
                        break
                if lowestValue == 0:
                    break
                if time.clock() - start > 600:
                    break
            
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
