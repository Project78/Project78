'''
Created on 29 nov. 2011

@author: Tom
'''
from google.appengine.api import mail
from google.appengine.api import users

class Mail():
    def __init__(self):
        pass
    
    def post(self):
        user = users.get_current_user()
        if user is None:
            login_url = users.create_login_url(self.request.path)
            self.redirect(login_url)
            return
        to_addr = self.request.get("t.nieuwenhuys@hotmail.com")
        if not mail.is_email_valid(to_addr):
            # Return an error message...
            pass

        message = mail.EmailMessage()
        message.sender = user.email()
        message.to = to_addr
        message.body = """
I've invited you to Example.com!

To accept this invitation, click the following link,
or copy and paste the URL into your browser's address
bar:

%s
        """        
