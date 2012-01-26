'''
Created on Dec 20, 2011

@author: averaart
'''

import itertools

from sets import Set
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api.datastore import Key
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


class test(webapp.RequestHandler):
    def get(self):
        table = [None, 2, 5, 7, None, None, None, None, None, 4, None, 3, 7, None, None]
        consecutiveNone = [len(list(y)) for (c,y) in itertools.groupby(table) if c==None]
        if len(consecutiveNone) > 0:
            print max(consecutiveNone)
        
        
#        Overzicht van docenten met aantal vak/klas combinaties
        
#        teachers = Teacher.all().fetch(999)
#        for i, teacher in enumerate(teachers):
#            combinations = Combination.all().filter("teacher", teacher).fetch(999)
#            requests = []
#            for comb in combinations:
#                requests += Request.all().filter("combination", comb).fetch(999)
#                
#            try:
#                calc = len(requests)/len(combinations)
#            except:
#                calc = 0
#            print str.ljust(str(i),3)+" "+\
#                    str.ljust(str(teacher.key().name()), 7)+\
#                    " - combinations: "+\
#                    str.ljust(str(len(combinations)),5)+\
#                    " - requests: "+\
#                    str.ljust(str(len(requests)),5)+\
#                    " - requests per combination: "+\
#                    str.ljust(str(calc),5)



#        Alle klassen en diens vakken
        
#        klassen = [str(comb.class_id) for comb in combinations]
#        klassen = set(klassen)
#        klassen = list(klassen)
#        klassen.sort()
#        
#        for klas in klassen:
#            combinations = Combination.all().filter("class_id", klas).fetch(999)
#            print klas
#            for comb in combinations:
#                print str.ljust(str(comb.subject.name), 20) +" "+ str(comb.teacher.key().name()) +" "+ str(comb.teacher.name) 
#            print ""




