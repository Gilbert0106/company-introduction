from datetime import date
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
import os.path

class Report(object):

    w, h = A4

    def __init__(self, ticker):
        self.ticker = ticker
        self.filepath = "reports/" + ticker + "-" + \
            date.today().strftime("%d%m%y") + ".pdf"

        if os.path.isfile(self.filepath):
            raise Exception(
                "A report for this ticker has already been generated today")

        # Create first page
        self.new_page()

    def add_title(self, name):
        self.canvas.setFont(psfontname='Times-Roman', size=24)
        self.canvas.drawString(32, self.h - 50, f'Introduction of:  {name} ({self.ticker})')

    def add_business_summary(self, summary):
        self.canvas.setFont(psfontname='Times-Roman', size=12)
        self.canvas.drawString(32, self.h - 82, summary)

    def add_footer(self):
        self.canvas.setFont(psfontname='Times-Roman', size=12)
        self.canvas.drawString(self.w - 72, 32, f'Page {self.pages_count}.')

    def new_page(self):
        if not hasattr(self, 'canvas'):
            # Create first page
            self.pages_count = 1
            self.canvas = Canvas(self.filepath, pagesize=A4)
        else:
            self.canvas.showPage()
            self.pages_count += 1

        self.add_footer()

    def save(self):
        self.canvas.save()
