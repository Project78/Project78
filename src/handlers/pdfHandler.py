
import sys
sys.path.insert(0, 'reportlab.zip')
from reportlab.pdfgen import canvas

from google.appengine.ext import webapp

class PDFHandler(webapp.RequestHandler):
    def get(self):
        text = 'hkjh dhkjfhkjdgh kdfhg hkdg '
        if text:
            p = canvas.Canvas(self.response.out)
            p.drawString(50, 700, 'The text you entered: ' + text)
            p.showPage()

            self.response.headers['Content-Type'] = 'application/pdf'
            self.response.headers['Content-Disposition'] = 'filename=testpdf.pdf'

            p.save()
