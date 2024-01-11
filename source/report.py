import os.path
from datetime import date

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

from source.companyApi import CompanyApi


class Report(object):

    w, h = A4

    def __init__(self, company: CompanyApi) -> None:
        self.company = company
        self.filepath = "reports/" + self.company.getSymbol() + "-" + \
            date.today().strftime("%d%m%y") + ".pdf"

        if os.path.isfile(self.filepath):
            raise Exception(
                "A report for this ticker has already been generated today")

        pdfmetrics.registerFont(
            TTFont("Consola", r"fonts/Consolas-Font/CONSOLA.TTF"))

        self.style = getSampleStyleSheet()

        # Create first page
        self.newPage()
        self.addTitle()
        self.addBusinessSummary()

    def addTitle(self) -> None:
        self.canvas.setFont(psfontname='Times-Roman', size=24)
        self.canvas.drawString(32, self.h - 50, "Introduction of: %s (%s)" %
                               (self.company.getName(), self.company.getSymbol()))

    def addBusinessSummary(self) -> None:
        string = '<font name="Consola size="16">' + self.company.getSummary() + '</font>'
        p = Paragraph(string, style=self.style["Normal"])
        p.wrapOn(self.canvas, self.w - 64, self.h)
        p.drawOn(self.canvas, 32, self.h - 280)

    def addFooter(self) -> None:
        self.canvas.setFont(psfontname='Times-Roman', size=12)
        self.canvas.drawString(self.w - 72, 32, f'Page {self.pagesCount}.')

    def newPage(self) -> None:
        if not hasattr(self, 'canvas'):
            # Create first page
            self.pagesCount = 1
            self.canvas = Canvas(self.filepath, pagesize=A4)
        else:
            self.canvas.showPage()
            self.pagesCount += 1

        self.addFooter()

    def save(self) -> None:
        self.canvas.save()
