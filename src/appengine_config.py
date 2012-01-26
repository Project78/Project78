'''
Created on Jan 26, 2012

@author: Maarten
'''
from gaesessions import SessionMiddleware
def webapp_add_wsgi_middleware(app):
    app = SessionMiddleware(app, cookie_key="eea985015e6f0475e02f1317a0ffa4beeaa044a7173dd5822cee16f75ff8f1b8ce91357a99245ed850c6c7a28342f05dbf9a6587866bc925d46fa98ae14eca2d")
    return app

