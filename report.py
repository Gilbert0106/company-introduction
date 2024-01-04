from datetime import date
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4


class Report(object):

    w, h = A4

    def __init__(self, ticker):
        self.ticker = ticker
        self.path = "reports/" + ticker + "-" + date.today().strftime("%d%m%y") + ".pdf"

    def canvas(self, size):
        self.canvas = Canvas(self.path, pagesize=A4)

    def title(self, name):
        self.canvas.drawString(72, self.h - 50, name)

    def save(self): 
        self.canvas.save()
