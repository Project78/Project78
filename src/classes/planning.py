'''
Created on Nov 27, 2011

@author: averaart
'''

class Planning(object):
    '''
    Collects all relevant data for an event for one guardian
    '''
    days=[]


    def __init__(self, event, days):
        '''
        Constructor
        '''
        for day in days:
            tables=[]
            for j in range(event.tables):
                slots=[]
                for i in range(day.talks):
                    slots.append(None)
                tables.append(slots)
            self.days.append(tables)    
                    
#                    
#            slots=[]
#            for i in range(day.talks):
#                tables=[]
#                for j in range(event.tables):
#                    tables.append(None)
#                slots.append(tables)
#            self.days.append(slots)

    def findNext(self, day_num, length, reverse):
        day = self.days[day_num]
        # eerste lege periode voor ieder tafel in een dag
        nextEmpty = [table.index(None) for table in day]
        myTable = nextEmpty.index(min(nextEmpty))
        
        return myTable
        
        
    def place(self, guardian, day_num):
        length = len(guardian.requests)
        nextTable = self.findNext(day_num, length, False)
        print nextTable
        startingIndex = self.days[day_num][nextTable].index(None)
        
        for requestIndex, tableIndex in enumerate(range(startingIndex, startingIndex+length)):
#            self.days[day_num][nextTable][tableIndex] = guardian.requests[requestIndex].combination.subject.name
            self.days[day_num][nextTable][tableIndex] = guardian.requests[requestIndex]
        
        
        
        
        return True
        
        