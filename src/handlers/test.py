'''
Created on Dec 20, 2011

@author: averaart
'''


from sets import Set
from google.appengine.ext import webapp
from google.appengine.ext import db
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
        print ""
        
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


        combinations = db.GqlQuery("SELECT * FROM Combination WHERE class_id >= :1 AND class_id < :2", "3", u"3" + u"\ufffd").fetch(9999)
        
        combinations.extend(db.GqlQuery("SELECT * FROM Combination WHERE class_id >= :1 AND class_id < :2", "4", u"4" + u"\ufffd").fetch(9999))
        
        teachers = [];
        
        for comb in combinations:
            teachers.append(comb.teacher.key().name())
        
        teachers = Set(teachers)
        
        for teacher in teachers:
            print teacher
            
        
        
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




