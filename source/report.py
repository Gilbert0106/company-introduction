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

        try:
            self.path = self.createPath(ticker=self.company.getSymbol())
            self.style = self.createStyle(
                fontName="Consola", fontPath=r"fonts/Consolas-Font/CONSOLA.TTF")
        except Exception as e:
            raise Exception(e)

        self.newPage()
        self.addTitle()
        self.y = self.addBusinessSummary(80)
        self.addBoxColumn(data=self.company.getIntroductoryMetrics(), y=self.y)

    def createPath(self, ticker: str) -> str:
        filepath = f'reports/{ticker}-{date.today().strftime("%d%m%y")}.pdf'

        if os.path.isfile(path=filepath):
            raise Exception(
                "A report for ticker " + ticker + " has already been generated today")

        return filepath

    def createStyle(self, fontName: str, fontPath: str) -> list:
        if not os.path.isfile(path=fontPath):
            raise Exception("The font can not be loaded from: " + fontPath)

        # Register font
        pdfmetrics.registerFont(
            TTFont(name=fontName, filename=fontPath))

        # Set style sheet
        style = getSampleStyleSheet()['Normal']
        style.fontName = "Consola"
        style.leading = 15
        return style

    def addTitle(self) -> int:
        self.style.fontSize = 9
        self.style.textColor = HexColor("#666666")
        p = Paragraph(date.today().strftime("%dth of %B %Y")
                      + ", Introduction of:", style=self.style)
        p.wrapOn(self.canvas, self.w - 64, self.h)
        p.drawOn(self.canvas, 32, self.h - p.height - 25)

        self.style.fontSize = 20
        self.style.textColor = HexColor("#000000")
        p = Paragraph("%s (%s)" %
                      (self.company.getName(), self.company.getSymbol()), style=self.style)
        p.wrapOn(self.canvas, self.w - 64, self.h)
        p.drawOn(self.canvas, 32, self.h - p.height - 45)

        return self.h - p.height - 45

    def addBusinessSummary(self, y: int) -> int:
        self.style.fontSize = 9
        p = Paragraph(self.company.getSummary(), style=self.style)
        p.wrapOn(canv=self.canvas, aW=self.w - 64, aH=self.h - y - 32)
        p.drawOn(canvas=self.canvas, x=32, y=self.h - y - p.height)

        return self.h - y - p.height

    def addBoxColumn(self, data: list, y: int, height=60, spacing=20) -> int:
        x = 32
        y = y - height - spacing
        width = self.w / len(data) - 100 / len(data)

        for item in data:
            self.drawBox(heading=item['value'], subtext=item['description'], x=x, y=y, height=height, width=width)
            x += (self.w - 64) / len(data)
        return

    def drawBox(self, heading: str, subtext: str, x: int, y: int, width: int, height: int) -> None:
        self.canvas.setStrokeColor(HexColor("#ffffff"))
        self.canvas.setFillColor(HexColor("#f5f5f5"))
        self.canvas.rect(x, y, width, height, fill=True)

        self.style.fontSize = 14
        heading_text = Paragraph(heading, style=self.style)
        heading_text.wrapOn(self.canvas, width, height)
        heading_text.drawOn(self.canvas, x + 10, y +
                            height - heading_text.height - 12)

        self.style.fontSize = 5
        subtext_text = Paragraph(subtext, style=self.style)
        subtext_text.wrapOn(self.canvas, width - 20,
                            height - heading_text.height - 10)
        subtext_text.drawOn(self.canvas, x + 10, y + 10)

    def addFooter(self) -> None:
        pageNumber = Paragraph(f'Page {self.pagesCount}.', style=self.style)
        pageNumber.wrapOn(self.canvas, 72, 72)
        pageNumber.drawOn(canvas=self.canvas, x=self.w - 72, y=20)

    def newPage(self) -> None:
        if not hasattr(self, 'canvas'):
            self.pagesCount = 1
            self.canvas = Canvas(self.path, pagesize=A4)
        else:
            self.canvas.showPage()
            self.pagesCount += 1

        self.addFooter()

    def save(self) -> None:
        self.canvas.save()
