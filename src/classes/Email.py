'''
Created on 27 jan. 2012

@author: Tom
'''

from google.appengine.api import mail
from google.appengine.api import users

from classes.CreatePDF import CreatePDF

class Email(object):
    def sendMail(self, addresses, title, text, attach = ''):
        user = users.get_current_user()
        if user is None:
            login_url = users.create_login_url(self.request.path)
            self.redirect(login_url)
            return
        
        for to_addr in addresses:
            to_addr = to_addr.strip()
            if mail.is_email_valid(to_addr):  
                message = mail.EmailMessage()
                message.sender = user.email()
                message.to = to_addr
                message.subject = title
                message.body = text
                if not attach == '':
                    pdf = CreatePDF().createPDF(attach)
                    if not pdf == None:
                        message.attachments = [(title + '.pdf', pdf)]
                message.Send()
                
