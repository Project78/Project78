
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail
from google.appengine.api import users

class MailHandler(webapp.RequestHandler):
    title = ''
    text = ''
    
    def get(self):
        path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-mail.html')
        
        template_values = {
            'title': self.title,
            'text': self.text
        }
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        
        if self.request.POST['i-send-mail']:
            self.title = self.request.POST['i-title']
            self.text = self.request.POST['i-text']
            
            user = users.get_current_user()
            if user is None:
                login_url = users.create_login_url(self.request.path)
                self.redirect(login_url)
                return
            to_addr = "t.nieuwenhuys@hotmail.com"
            if not mail.is_email_valid(to_addr):
                print 'ERROR!!!'
                pass
    
            message = mail.EmailMessage()
            message.sender = user.email()
            message.to = to_addr
            message.subject = self.title
            message.body = self.text       
            message.Send()
            
            print 'title = ' + self.title + '\ntext = ' + self.text