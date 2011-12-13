
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail
from google.appengine.api import users

class MailHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), '../templates/administration/event-mail.html')

        self.response.out.write(template.render(path, {}))
        
    def post(self):
        
        if self.request.POST['i-send-mail']:
            title = self.request.POST['i-title']
            text = self.response.POST['i-text']
            
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
            message.subject = title
            message.body = text       
            message.Send()