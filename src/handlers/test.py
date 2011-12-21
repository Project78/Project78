'''
Created on Dec 20, 2011

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


class test(webapp.RequestHandler):
    def get(self):
        print ""
        teachers = Teacher.all().fetch(999)
        for i, teacher in enumerate(teachers):
            combinations = Combination.all().filter("teacher", teacher).fetch(999)
            requests = []
            for comb in combinations:
                requests += Request.all().filter("combination", comb).fetch(999)
                
            try:
                calc = len(requests)/len(combinations)
            except:
                calc = 0
            print str.ljust(str(i),3)+" "+\
                    str.ljust(str(teacher.key().name()), 7)+\
                    " - combinations: "+\
                    str.ljust(str(len(combinations)),5)+\
                    " - requests: "+\
                    str.ljust(str(len(requests)),5)+\
                    " - requests per combination: "+\
                    str.ljust(str(calc),5)


