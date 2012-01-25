'''
Created on 24 jan. 2012

@author: Tom
'''

class Attachment(object):
    name = 'name'
    read = 'read'
    
    def __init__(self, file):
        f = open(file, 'r');
        self.name = f.name
        self.read = f.read()
        