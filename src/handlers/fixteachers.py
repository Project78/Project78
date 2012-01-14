'''
Created on Dec 20, 2011

@author: averaart
'''


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


class FixTeachers(webapp.RequestHandler):
    def get(self):
        print ""
                
        combinations = db.GqlQuery("SELECT * FROM Combination WHERE class_id >= :1 AND class_id < :2", "3", u"3" + u"\ufffd").fetch(9999)
        combinations.extend(db.GqlQuery("SELECT * FROM Combination WHERE class_id >= :1 AND class_id < :2", "4", u"4" + u"\ufffd").fetch(9999))
        
        # All teachers that are assigned to a subject
        workingTeachers = [];
        
        for comb in combinations:
            workingTeachers.append(comb.teacher.key().name())
        
        workingTeachers = Set(workingTeachers)
        workingTeachers = list(workingTeachers)

        
        # Teachers not assigned to a subject        
        temp = Teacher.all().fetch(9999)
        otherTeachers = [teacher.key().name() for teacher in temp]
        
        for teacher in workingTeachers:
            otherTeachers.remove(teacher)
        
        groupA = otherTeachers[:40]
        groupB = otherTeachers[37:]

        
        # Get all combinations for years 3 and 4
        
        combinations = db.GqlQuery("SELECT * FROM Combination WHERE class_id >= :1 AND class_id < :2", "3", u"3" + u"\ufffd").fetch(9999)
        combinations.extend(db.GqlQuery("SELECT * FROM Combination WHERE class_id >= :1 AND class_id < :2", "4", u"4" + u"\ufffd").fetch(9999))
        
        print "Conversion for years 3 and 4:"
        
        for comb in combinations:
            oldTeacher = comb.teacher.key().name()
            oldTeacherIndex = workingTeachers.index(oldTeacher)
            newTeacherKey = groupA[oldTeacherIndex]
            newTeacher = Teacher.all().filter("__key__", Key.from_path('Teacher',newTeacherKey)).get()
            print "old: "+oldTeacher+" - new: "+newTeacher.key().name()
            comb.teacher = newTeacher
            comb.save()
        
        
        # Get all combinations for years 5 and 6
        
        combinations = db.GqlQuery("SELECT * FROM Combination WHERE class_id >= :1 AND class_id < :2", "5", u"5" + u"\ufffd").fetch(9999)
        combinations.extend(db.GqlQuery("SELECT * FROM Combination WHERE class_id >= :1 AND class_id < :2", "6", u"6" + u"\ufffd").fetch(9999))
        
        # All teachers that are assigned to a subject
        workingTeachers = [];
        
        for comb in combinations:
            workingTeachers.append(comb.teacher.key().name())
        
        workingTeachers = Set(workingTeachers)
        workingTeachers = list(workingTeachers)        
        
        combinations = db.GqlQuery("SELECT * FROM Combination WHERE class_id >= :1 AND class_id < :2", "5", u"5" + u"\ufffd").fetch(9999)
        combinations.extend(db.GqlQuery("SELECT * FROM Combination WHERE class_id >= :1 AND class_id < :2", "6", u"6" + u"\ufffd").fetch(9999))
        
        
        print "Conversion for years 5 and 6:"
        
        for comb in combinations:
            oldTeacher = comb.teacher.key().name()
            oldTeacherIndex = workingTeachers.index(oldTeacher)
            newTeacherKey = groupB[oldTeacherIndex]
            newTeacher = Teacher.all().filter("__key__", Key.from_path('Teacher',newTeacherKey)).get()
            print "old: "+oldTeacher+" - new: "+newTeacher.key().name()
            comb.teacher = newTeacher
            comb.save()




