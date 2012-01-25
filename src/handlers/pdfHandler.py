# testpdf.py - test PDF generator

from reportlab.pdfgen import canvas

from google.appengine.ext import webapp

class PDFHandler(webapp.RequestHandler):
    def get(self):
#        text = self.request.get('t')
        text = 'random'
        if text:
            p = canvas.Canvas(self.response.out)
#            p.drawImage('dog.jpg', 150, 400)
            p.drawString(50, 700, 'The text you entered: ' + text)
            p.showPage()

            self.response.headers['Content-Type'] = 'application/pdf'
            self.response.headers['Content-Disposition'] = 'filename=testpdf.pdf'

            p.save()

