import os.path
from datetime import date

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
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

        self.style = getSampleStyleSheet()['Normal']
        self.style.fontName = "Consola"
        self.style.leading = 15

        # Create first page
        self.newPage()
        self.addTitle()
        self.addBusinessSummary()

    def addTitle(self) -> None:
        self.style.fontSize = 9
        self.style.textColor = HexColor("#666666")
        p = Paragraph(date.today().strftime("%dth of %B %Y")
                      + ", Introduction of:", style=self.style)
        p.wrapOn(self.canvas, self.w - 64, self.h)
        p.drawOn(self.canvas, 32, self.h - p.height - 20)

        self.style.fontSize = 20
        self.style.textColor = HexColor("#000000")
        p = Paragraph("%s (%s)" %
                      (self.company.getName(), self.company.getSymbol()), style=self.style)
        p.wrapOn(self.canvas, self.w - 64, self.h)
        p.drawOn(self.canvas, 32, self.h - p.height - 40)

    def addBusinessSummary(self) -> None:
        self.style.fontSize = 9
        p = Paragraph(self.company.getSummary(), style=self.style)
        p.wrapOn(self.canvas, self.w - 64, self.h)
        p.drawOn(self.canvas, 32, self.h - p.height - 80)

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
