'''
Created on Jan 26, 2012

@author: Maarten
'''
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from handlers.plan import plan
from handlers.administration import AdministrationIndexHandler
from handlers.administration import AdministrationEventListHandler
from handlers.administration import AdministrationEventEditHandler

def main():
    application = webapp.WSGIApplication(
        [('/administratie/event/(\d+)/genereer-planning/?', plan),
        ('/administratie/event/(nieuw|\d+)/?', AdministrationEventEditHandler),
        ('/administratie/events/?', AdministrationEventListHandler),
        ('/administratie/?', AdministrationEventListHandler),
        ('/admin/?', AdministrationIndexHandler)
        ], debug=True
    )
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
