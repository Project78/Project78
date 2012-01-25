
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail
from google.appengine.api import users

from models.guardian import Guardian
from models.teacher import Teacher
from classes.attachment import Attachment

import sys
sys.path.insert(0, 'reportlab.zip')
from reportlab.pdfgen import canvas

class MailHandler(webapp.RequestHandler):
    title = 'title'
    text = 'text'
    
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
                if self.request.POST['attach']:
                    attach = self.request.POST['attach']
                    attachments = []
                    for attachment in attach.split(';'):
                        attachments.append(Attachment(attachment))
            except KeyError:
                attachments = False
                
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
                if not mail.is_email_valid(to_addr):
                    print to_addr + ' is not a valid e-mail address'
                else:
                    att = []
                    if not attachments == False:
                        for attachment in attachments:
                            att.append((attachment.name, attachment.read))
                        
                    message = mail.EmailMessage()
                    message.sender = user.email()
                    message.to = to_addr
                    message.subject = self.title
                    message.body = self.text
                    if len(att) > 0:
                        message.attachments = att
                    message.Send()
                    
#                    print 'mail send to ' + to_addr
            
            self.createPDF()
    
    def createPDF(self):
        if not self.text == 'text':
            p = canvas.Canvas(self.response.out)
#            p.drawImage('dog.jpg', 150, 400)
            p.drawString(50, 700, 'The text you entered: ' + self.text)
            p.showPage()

            self.response.headers['Content-Type'] = 'application/pdf'
            self.response.headers['Content-Disposition'] = 'filename=' + self.title + '.pdf'

            p.save()
                    
            