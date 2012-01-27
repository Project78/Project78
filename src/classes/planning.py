'''
Created on Nov 27, 2011

@author: averaart
'''

import random
import itertools

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
            longestContinuous = [len(list(y)) for (c,y) in itertools.groupby(table) if c==None]
            if len(longestContinuous) == 0:
                nextEmpty = 999
            elif max(longestContinuous) < length+1:
#            if max(len(list(y)) for (c,y) in itertools.groupby(table) if c==None) < length:
                nextEmpty[i] = 999
        
        if min(nextEmpty) == 999:
            return 999
            
        myTable = nextEmpty.index(min(nextEmpty))
        
        return myTable
        
    def place(self, guardian, day_num):
        length = len(guardian.requests)
        
        # Make sure a teacher doesn't get too many appointments in one day
        for request in guardian.requests:
            if self.appointmentsPerDay(day_num, request.combination.teacher.key().name()) >= len(self.days[day_num][0]):
                return False
        
        if guardian.time_pref.preference == 2:
            reversed = True
        else:
            reversed = False
        
        nextTable = self.findNext(day_num, length, reversed)
        if nextTable == 999:
            return False
        
        nextTable = self.days[day_num][nextTable]
        if (reversed):
            for slotIndex, slot in enumerate(reverse(nextTable)):
                if nextTable[slotIndex] == None and nextTable[slotIndex-1] == None:
                    startingIndex = len(nextTable)-length-slotIndex-1
                    break
#                startingIndex = len(nextTable)-length-reverse(nextTable).index(None)
        else:
#            startingIndex = nextTable.index(None)
            for slotIndex, slot in enumerate(nextTable):
                if nextTable[slotIndex] == None and nextTable[slotIndex+1] == None:
                    startingIndex = slotIndex+1
                    break
                
            
        for requestIndex, slotIndex in enumerate(range(startingIndex, startingIndex+length)):
            nextTable[slotIndex] = guardian.requests[requestIndex]
            nextTable[slotIndex].moveCounter=0
            nextTable[slotIndex].startingPosition=slotIndex
            
        
        return True
        
    def nextNone(self, list):
        try:
            result = list.index(None)+1
        except:
            result = 999
        return result


    def conflictedTeachers(self, day, slotnumber):
        sideways = zip(*day)
        print "ontvangen slotnummer: "+str(slotnumber)+"<br>"
        slot = filter(lambda x: x != None, sideways[slotnumber])
        teachersInSlot = [table.combination.teacher.key().name() for table in slot]
        uniqueTeachers = set([table.combination.teacher.key().name() for table in slot])
        countAppointments = [teachersInSlot.count(teacher) for teacher in uniqueTeachers]
        conflicted = []
        for i, teacher in enumerate(uniqueTeachers):
            if countAppointments[i] > 1:
                conflicted.append(teacher)

#        print "conflictedTeachers called for slot "+str(slotnumber)
#        print "all teachers in slot: "+str(teachersInSlot)
#        print "unique teachers in slot: "+str(uniqueTeachers)
#        print "number of appointments per unique teacher: "+str(countAppointments)
#        print ""

        
        return conflicted
    
    def flipped(self, day):
        return zip(*day)

    def getTeacherStringFromRequest(self, request):
            if request == None:
                return ""
            else:
                return request.combination.teacher.key().name()

    def getGuardianIdFromRequest(self, request):
            if request == None:
                return ""
            else:
                return request.guardian.key().name()

    def appointmentsPerDay(self, dayNum, teacher):
        slots = []
        for table in self.days[dayNum]:
            for slot in table:
                slots.append(self.getTeacherStringFromRequest(slot))
        return slots.count(teacher)
        
    def getMoveCounter(self, request):
            if request == None:
                return 0
            else:
                return request.moveCounter

    def getStartingPosition(self, request):
            if request == None:
                return 99999
            else:
                return request.startingPosition

    def pprint(self):
        for i, day in enumerate(self.days):
            print "Day: "+(str)(i+1)
            for table in day:
                text = ""
                for slot in table:
                    if slot is None:
                        text += str.ljust("-", 12)
                    else:
                        text += str.ljust(str(slot.guardian.key().name())+":"+str(slot.combination.teacher.key().name()), 12)
                print text
        print ""

    def pprint_day(self, day):
        for table in day:
            text = ""
            for slot in table:
                if slot is None:
                    text += str.ljust("-", 12)
                else:
                    text += str.ljust(str(slot.guardian.key().name())+":"+str(slot.combination.teacher.key().name()), 12)
            print text
        print ""
        
    def outputHTML(self):
        lb = "\n"
        tab = "    "
        result = ""
#        result += "<html><body style='font-family: Helvetica; font-size: 0.8em;'>"
        for i, day in enumerate(self.days):
            result += "Day: "+(str)(i+1)+lb
            result += "<table style='font-size: 0.8em;'>"+lb
            for table in day:
                result += "<tr>"+lb+tab
                for slot in table:
                    if slot is None:
                        result += "<td style='width: 75px; padding: 2px;'>"
                        result += str.ljust("-", 12)
                    else:
                        random.seed(int(slot.guardian.key().name()))
                        r = random.randint(0, 255)
                        g = random.randint(0, 255)
                        b = random.randint(0, 255)
                        if r+b+g > 383:
                            t = 0
                        else:
                            t = 255
                        result += "<td style='width: 75px; text-align: center; padding: 2px; background: rgb("+str(r)+","+str(g)+","+str(b)+"); color: rgb("+str(t)+","+str(t)+","+str(t)+")'>"
                        result += str(slot.combination.teacher.key().name())+"<br>"+str(slot.guardian.key().name())
                    result += "</td> "
                result += "</tr>"+lb
            result += "</table>"+lb
        result +="</body></html>"+lb
#        result +="THIS_IS_A_SEPARATOR"+lb
        print result