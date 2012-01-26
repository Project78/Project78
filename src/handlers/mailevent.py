
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail
from google.appengine.api import users

from models.guardian import Guardian
from models.teacher import Teacher
from classes.CreatePDF import CreatePDF

class MailHandler(webapp.RequestHandler):
    title = 'title'
    text = 'text'
    attach = ''
    
    def get(self):
        path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-mail.html')
        
        self.response.out.write(template.render(path, {}))
        
    def post(self):        
        if self.request.POST['send-mail']:
            addresses = False
            if self.request.POST['title']:
                self.title = self.request.POST['title']
            if self.request.POST['text']:
                self.text = self.request.POST['text']
            if self.request.POST['target'] == 'Specific address(es)':
                address = self.request.POST['addresses']
                addresses = address.split(';')
            try:
                self.attach = self.request.POST['attach']
            except KeyError:
                self.attach = ''
                
            user = users.get_current_user()
            if user is None:
                login_url = users.create_login_url(self.request.path)
                self.redirect(login_url)
                return
            
            if not addresses:
                addresses = []
                if self.request.POST['target'] == 'All guardians':
                    guardians = Guardian.all()
                    for guardian in guardians:
                        addresses.append(guardian.email)
                elif self.request.POST['target'] == 'All teachers':
                    teachers = Teacher.all()
                    for teacher in teachers:
                        addresses.append(teacher.email)
            
            for to_addr in addresses:
                to_addr = to_addr.strip()
                if mail.is_email_valid(to_addr):  
                    message = mail.EmailMessage()
                    message.sender = user.email()
                    message.to = to_addr
                    message.subject = self.title
                    message.body = self.text
                    if not self.attach == '':
                        pdf = CreatePDF().createPDF(self.attach)
                        if not pdf == None:
                            message.attachments = [(self.title + '.pdf', pdf)]
#                            print pdf
                    message.Send()
                    print 'E-mail send to %s' % to_addr
    