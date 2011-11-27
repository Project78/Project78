import os
import re
import time
import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

class NewEvent(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-new.html')
        self.response.out.write(template.render(path, {}))
    
    def post(self):
        n = self.request.POST['i-name']
        d = self.request.POST['i-startdate']
        v = Validator()
        errors = [];
        
        if not v.vString(n):
            errors.append('onjuiste titel ouderavondreeks')        
        if not v.vDate(d):
            errors.append('onjuiste startdatum')
        
        if errors:
            path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-new.html')
            tv = { 'errors': errors }
            self.response.out.write(template.render(path, tv))
            return
        else:
            return
            #d = map(int, (d.split('-')))
            #date = datetime.datetime(year=d[0], month=d[1], day=d[2], hour=20, minute=00)
            
        
class Validator:
    def vDate(self, d):
        if re.match(r'\d{4}-\d{2}-\d{2}', d):
            return True
        else:
            return False
    
    def vString(self, s):
        if s:
            return True
        else:
            return False
