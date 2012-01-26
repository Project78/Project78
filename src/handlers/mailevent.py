
import os
import sys

sys.path.insert(0, 'reportlab.zip')

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail
from google.appengine.api import users

from models.guardian import Guardian
from models.teacher import Teacher

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

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
                        pdf = self.createPDF(self.attach)
                        if not pdf == None:
                            message.attachments = [(self.title + '.pdf', pdf)]
#                            print pdf
                    message.Send()
                    print 'E-mail send to %s' % to_addr
                    
    def createPDF(self, text):
        if not text.strip() == '':
            buf = StringIO()
            p = canvas.Canvas(buf, pagesize=A4)
            p.setFont('Helvetica-Bold', 20)
            p.drawString(50, 780, "Donald Knuth College")
            p.line(50, 774, 540, 774)
            
            parts = text.split('\n')
            p.setFont('Helvetica', 10)
            i = 0
            jump = 16
            limit = 750
            lineWidth = 110
            
            for part in parts:
                if i + 60 <= limit:
                    part = part.strip();
                    pts = part.split(' ')
                    s = ''
                    for pt in pts:
                        if len(s) + len(pt) < lineWidth:
                            s += pt + ' '
                        else:
                            if i + 60 <= limit:
                                p.drawString(50, limit - i, s.strip())
                                s = pt + ' '
                                i += jump
                            else:
                                self.nextPage(p)
                                p.drawString(50, limit, s.strip())
                                s = pt + ' '
                                i = jump
                    
                    p.drawString(50, limit - i, s.strip())
                    i += jump
                else:
                    self.nextPage(p)
                    p.drawString(50, limit, part.strip())
                    i = jump

            p.save()
            pdf = buf.getvalue()
            buf.close() 
            return pdf
        else:
            return None
        
    def nextPage(self, p):
        p.showPage()
        p.setFont('Helvetica-Bold', 20)
        p.drawString(50, 780, "Donald Knuth College")
        p.line(50, 774, 540, 774)
        p.setFont('Helvetica', 10)
    