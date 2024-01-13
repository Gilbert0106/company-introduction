import os.path
from datetime import date

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

from source.companyApi import CompanyApi


class Report(object):

    w, h = A4

    def __init__(self, company: CompanyApi) -> None:
        self.company = company

        try:
            self.path = self.createPath(ticker=self.company.getSymbol())
            self.style = self.createStyle(
                fontName="Consola", fontPath=r"fonts/Consolas-Font/CONSOLA.TTF")
            self.margin = 32
        except Exception as e:
            raise Exception(e)

        self.newPage()
        self.addTitle()
        self.y = self.addBusinessSummary(80)
        self.y = self.addBoxColumn(
            data=self.company.getIntroductoryMetrics(), y=self.y)
        self.addBarChart(data=self.company.getBarChartData(), y=self.y)

        # Next page

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

    def newPage(self) -> None:
        if not hasattr(self, 'canvas'):
            self.pagesCount = 1
            self.canvas = Canvas(self.path, pagesize=A4)
        else:
            self.canvas.showPage()
            self.pagesCount += 1

        self.addFooter()

    def addFooter(self) -> None:
        pageNumber = Paragraph(f'Page {self.pagesCount}.', style=self.style)
        pageNumber.wrapOn(self.canvas, 72, 72)
        pageNumber.drawOn(canvas=self.canvas, x=self.w - 72, y=20)

    def addTitle(self) -> int:
        self.style.fontSize = 9
        self.style.textColor = HexColor("#666666")
        p = Paragraph(date.today().strftime("%dth of %B %Y")
                      + ", Introduction of:", style=self.style)
        p.wrapOn(self.canvas, self.w - self.margin * 2, self.h)
        p.drawOn(self.canvas, self.margin, self.h - p.height - 25)

        self.style.fontSize = 20
        self.style.textColor = HexColor("#000000")
        p = Paragraph("%s (%s)" %
                      (self.company.getName(), self.company.getSymbol()), style=self.style)
        p.wrapOn(self.canvas, self.w - self.margin * 2, self.h)
        p.drawOn(self.canvas, self.margin, self.h - p.height - 45)

        return self.h - p.height - 45

    def addBusinessSummary(self, y: int) -> int:
        self.style.fontSize = 9
        p = Paragraph(self.company.getSummary(), style=self.style)
        p.wrapOn(canv=self.canvas, aW=self.w -
                 self.margin * 2, aH=self.h - y - self.margin)
        p.drawOn(canvas=self.canvas, x=self.margin, y=self.h - y - p.height)

        return self.h - y - p.height

    def addBoxColumn(self, data: list, y: int, height=60, spacing=20) -> int:
        x = self.margin
        y = y - height - spacing
        width = self.w / len(data) - 100 / len(data)

        for item in data:
            self.drawBox(
                heading=item['value'], subtext=item['description'], x=x, y=y, height=height, width=width)
            x += (self.w - self.margin * 2) / len(data)
        
        return y

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

    def addBarChart(self, data: list, y: int) -> None:
        # Add a heading
        self.style.fontSize = 16
        heading = Paragraph("Bar chart heading", self.style)
        heading.wrapOn(self.canvas, self.w, self.h)
        heading.drawOn(self.canvas, self.margin, y - 40)

        # Add helptext
        self.style.fontSize = 9
        self.style.textColor = HexColor("#666666")
        p = Paragraph("Lorem ipsum dolor set ami", style=self.style)
        p.wrapOn(self.canvas, self.w - self.margin * 2, self.h)
        p.drawOn(self.canvas, self.margin, y - heading.height - p.height - 40)

        # Create a ReportLab Drawing object
        drawing = Drawing(self.w - self.margin * 2, 200)

        # Create a bar chart
        chart = VerticalBarChart()
        chart.width = self.w - self.margin * 3
        chart.height = y - self.margin * 2 - heading.height - 100
        chart.data = [[x[1] for x in data]]
        chart.categoryAxis.categoryNames = [str(x[0]) for x in data]

        # Add the bar chart to the drawing
        drawing.add(chart)

        # Draw the drawing on the canvas
        drawing.wrapOn(self.canvas, self.w - self.margin * 4, chart.height)
        drawing.drawOn(self.canvas, self.margin, self.margin * 2)

    def save(self) -> None:
        self.canvas.save()
