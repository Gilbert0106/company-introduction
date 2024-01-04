from datetime import date
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
import os.path


class Report(object):

    w, h = A4

    def __init__(self, ticker):
        self.ticker = ticker
        self.path = "reports/" + ticker + "-" + date.today().strftime("%d%m%y") + ".pdf"

        if os.path.isfile(self.path):
            raise Exception("A report for this ticker has already been generated today")
        
        self.create_canvas()

    def create_canvas(self):
        self.canvas = Canvas(self.path, pagesize=A4)

    def add_title(self, name):
        self.canvas.drawString(72, self.h - 50, "Introduction of: " + name)

    def save(self): 
        self.canvas.save()
