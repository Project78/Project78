'''
Created on Jan 26, 2012

@author: Maarten
'''
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from handlers.plan import plan
from handlers.administration import AdministrationEventListHandler
from handlers.administration import AdministrationEventEditHandler
from handlers.administration import AdministrationGenerateGuardianKeys
from handlers.administration import AdministrationInviteGuardiansHandler

def main():
    application = webapp.WSGIApplication(
        [('/administratie/event/(\d+)/verstuur-uitnodigingen', AdministrationInviteGuardiansHandler),
        ('/administratie/event/(\d+)/genereer-voogd-sleutels/?', AdministrationGenerateGuardianKeys),
        ('/administratie/event/(\d+)/genereer-planning/?', plan),
        ('/administratie/event/(nieuw|\d+)/?', AdministrationEventEditHandler),
        ('/administratie/events/?', AdministrationEventListHandler),
        ('/administratie/?', AdministrationEventListHandler),
        ], debug=True
    )
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
