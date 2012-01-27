
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail
from google.appengine.api import users

from models.guardian import Guardian
from models.teacher import Teacher
from classes.CreatePDF import CreatePDF
from classes.Email import Email

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
            
            Email().sendMail(addresses, self.title, self.text, self.attach)
            
            HTMLTEST = """
            <html><body>
            <p>Hello <strong style="color: #f00;">World</strong>
            <hr>
            <table border="1" style="background: #eee; padding: 0.5em;">
                <tr>
                    <td>Amount</td>
                    <td>Description</td>
                    <td>Total</td>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Good weather</td>
                    <td>0 EUR</td>
                </tr>
                <tr style="font-weight: bold">
                    <td colspan="2" align="right">Sum</td>
                    <td>0 EUR</td>
                </tr>
            </table>
            </body></html>
            """
            print CreatePDF().HTML2PDF(HTMLTEST, open=True)
    