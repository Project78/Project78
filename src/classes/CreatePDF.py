'''
Created on 26 jan. 2012

@author: Tom
'''

import sys
import os

sys.path.insert(0, 'reportlab.zip')
sys.path.insert(0, 'html5lib.zip')
sys.path.insert(0, 'xhtml2pdf.zip')

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from xhtml2pdf import pisa

from cStringIO import StringIO

class CreatePDF(object): 
    def HTML2PDF(self, data, open=False):

        result = StringIO()
        pdf = pisa.CreatePDF(StringIO(data), result)
        if open:
#            print "Content-type: application/pdf"
            return result.getvalue()
    
    def createPDF(self, text):
        if not text.strip() == '':
            buf = StringIO()
            p = canvas.Canvas(buf, pagesize=A4)
            p.setFont('Helvetica-Bold', 20)
            p.drawString(50, 780, "Donald Knuth College")
            p.line(50, 774, 540, 774)
            
            parts = text.split('\n')
            p.setFont('Helvetica', 10)
            i = 0
            jump = 16
            limit = 750
            lineWidth = 110
            
            for part in parts:
                if i + 60 <= limit:
                    part = part.strip();
                    pts = part.split(' ')
                    s = ''
                    for pt in pts:
                        if len(s) + len(pt) < lineWidth:
                            s += pt + ' '
                        else:
                            if i + 60 <= limit:
                                p.drawString(50, limit - i, s.strip())
                                s = pt + ' '
                                i += jump
                            else:
                                self.nextPage(p)
                                p.drawString(50, limit, s.strip())
                                s = pt + ' '
                                i = jump
                    
                    p.drawString(50, limit - i, s.strip())
                    i += jump
                else:
                    self.nextPage(p)
                    p.drawString(50, limit, part.strip())
                    i = jump

            p.save()
            pdf = buf.getvalue()
            buf.close() 
            return pdf
        else:
            return None
        
    def nextPage(self, p):
        p.showPage()
        p.setFont('Helvetica-Bold', 20)
        p.drawString(50, 780, "Donald Knuth College")
        p.line(50, 774, 540, 774)
        p.setFont('Helvetica', 10)