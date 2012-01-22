'''
Created on Nov 27, 2011

@author: averaart
'''

for n,m in ( ('reverse(o)','n.reverse()'),('sort(o)','n.sort()'),\
                ('extend(o,o1)','n.extend(o1)')): exec "def %s:\n t=type\n to=t(o)\
                \n if to in (t(''),t(())): n=list(o)\n else: n=to(o)\n %s\n return n and\
                (to==t('') and ''.join(n) or to==t(()) and tuple(n) or n) or to()\n" % (n,m)



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
                    
    def findNext(self, day_num, length, reversed):
        day = self.days[day_num]
        if (reversed):
            # laatste lege periode voor ieder tafel in een dag
            nextEmpty = [self.nextNone(reverse(table)) for table in day]
        else:
            # eerste lege periode voor ieder tafel in een dag
            nextEmpty = [self.nextNone(table) for table in day]
        
        for i, table in enumerate(day):
            if table.count(None) < length:
                nextEmpty[i] = 999
        
        if min(nextEmpty) == 999:
            return 999
            
        myTable = nextEmpty.index(min(nextEmpty))
        
        return myTable
        
    def place(self, guardian, day_num):
        length = len(guardian.requests)
        
        if guardian.time_pref.preference == 2:
            reversed = True
        else:
            reversed = False
        
        nextTable = self.findNext(day_num, length, reversed)
        if nextTable == 999:
            return False
        
        nextTable = self.days[day_num][nextTable]
        if (reversed):
            startingIndex = len(nextTable)-length-reverse(nextTable).index(None)
        else:
            startingIndex = nextTable.index(None)
            
        for requestIndex, tableIndex in enumerate(range(startingIndex, startingIndex+length)):
            nextTable[tableIndex] = guardian.requests[requestIndex]
        
        return True
        
    def nextNone(self, list):
        try:
            result = list.index(None)
        except:
            result = 999
        return result


