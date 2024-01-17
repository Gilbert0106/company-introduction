import os.path
from datetime import date

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.graphics.shapes import Drawing, Circle
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart

from source.companyApi import CompanyApi


class Report(object):

    w, h = A4

    def __init__(self, company: CompanyApi, overwrite: bool) -> None:
        self.company = company

        try:
            self.path = self.createPath(
                ticker=self.company.getSymbol(), overwrite=overwrite
            )
            self.style = self.createStyle(
                fontName="Consola", fontPath=r"fonts/Consolas-Font/CONSOLA.TTF"
            )
        except Exception as e:
            raise Exception(e)

        self.newPage()
        self.addTitle()
        self.y = self.addBusinessSummary(80)
        self.y = self.addBoxColumn(
            data=self.company.getIntroductoryMetrics(), y=self.y
        )
        self.addLineChart(
            profiles=self.company.getHistoricalPriceData(
                tickers=[
                    {
                        'ticker': '^GSPC',
                        'name': 'S&amp;P 500',
                        'color': '#F6BE00',
                    },
                    {
                        'ticker': '^DJI',
                        'name': 'Dow Jones Industrial Avg.',
                        'color': '#0044CC',
                    }
                ]
            ),
            y=self.y
        )

    def createPath(self, ticker: str, overwrite: bool) -> str:
        filepath = f'reports/{ticker}-{date.today().strftime("%d%m%y")}.pdf'

        if os.path.isfile(path=filepath) and not overwrite:
            raise Exception(
                "A report for ticker " + ticker +
                " has already been generated today. If you would like to overwrite the previous version you may run the program with --overwrite."
            )

        return filepath

    def createStyle(self, fontName: str, fontPath: str) -> list:
        if not os.path.isfile(path=fontPath):
            raise Exception("The font can not be loaded from: " + fontPath)

        self.margin = 32

        # Register font
        pdfmetrics.registerFont(
            TTFont(name=fontName, filename=fontPath)
        )

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
        self.canvas.setStrokeColorRGB(0, 0, 0)
        self.canvas.setLineWidth(1)

        self.canvas.line(32, 45, self.w - 32, 46)

        self.addText(
            text="Authored by Simon, https://github.com/Gilbert0106/company-introduction",
            size=9,
            color="#666666",
            x=self.w - 380,
            y=32.5,
            aW=self.w
        )

        self.addText(
            text=f'Page {self.pagesCount}.',
            size=9,
            x=32,
            y=32,
        )

    def addHeading2(self) -> None:
        return

    def addParagraph(self) -> None:
        return

    def addHeading1(self, text: str, y: int, x: int = None) -> int:
        if x is None:
            x = self.margin

        return self.addText(text=text, size=20, x=x, y=y)

    def addHeading2(self, text: str, y: int, x: int = None) -> int:
        if x is None:
            x = self.margin

        return self.addText(text=text, size=16, x=x, y=y)

    def addParagraph(self, text: str, y: int, x: int = None) -> int:
        if x is None:
            x = self.margin

        return self.addText(text=text, size=9, x=x, y=y)

    def addHelpText(self, text: str, y: int, x: int = None) -> int:
        if x is None:
            x = self.margin

        return self.addText(text=text, size=9, color="#666666", x=x, y=y)

    def addText(self, x: int, y: int, text: str, size: int, color: str = None, aW: int = None, aH: int = None) -> Paragraph:
        if color is None:
            color = "#000000"
        if aW is None:
            aW = self.w - x - self.margin
        if aH is None:
            aH = self.h

        self.style.fontSize = size
        self.style.textColor = HexColor(color)
        p = Paragraph(text, style=self.style)
        p.wrapOn(self.canvas, aW, aH)
        p.drawOn(self.canvas, x, y - p.height)

        return p.height

    def addTitle(self) -> int:
        self.addHelpText(
            text=date.today().strftime("%dth of %B %Y") + ", Introduction of:",
            y=self.h - 25
        )

        self.addHeading1(
            text="%s (%s)" % (self.company.getName(),
                              self.company.getSymbol()),
            y=self.h - 45
        )

        return self.h - 70

    def addBusinessSummary(self, y: int) -> int:
        return self.h - y - self.addParagraph(self.company.getSummary(), y=self.h - y)

    def addBoxColumn(self, data: list, y: int, height=60, spacing=20) -> int:
        x = self.margin
        y = y - height - spacing
        width = self.w / len(data) - 100 / len(data)

        for item in data:
            self.drawBox(
                heading=item['value'],
                subtext=item['description'],
                x=x,
                y=y,
                height=height,
                width=width
            )
            x += (self.w - self.margin * 2) / len(data)

        return y

    def drawBox(self, heading: str, subtext: str, x: int, y: int, width: int, height: int) -> None:
        self.canvas.setStrokeColor(HexColor("#ffffff"))
        self.canvas.setFillColor(HexColor("#f5f5f5"))

        self.canvas.rect(
            x=x,
            y=y,
            width=width,
            height=height,
            fill=True
        )

        self.addText(
            x=x + 10,
            y=y + height - 15,
            text=heading,
            size=14
        )

        self.addText(
            x=x + 10,
            y=y + 20,
            text=subtext,
            size=5,
            aW=width - 20
        )

    def addBarChart(self, data: list, y: int) -> None:
        # Add a heading 2
        headingHeight = self.addHeading2(
            text="Figure 1: Share price over time.",
            x=self.margin,
            y=y - 40
        )

        # Add helptext
        self.addHelpText(
            text="Lorem ipsum dolor set ami",
            y=y - headingHeight - 50
        )

        # Create a ReportLab Drawing object
        drawing = Drawing(
            width=self.w - self.margin * 2,
            height=200
        )

        # Create a bar chart
        chart = VerticalBarChart()
        chart.width = self.w - self.margin * 3
        chart.height = y - self.margin * 2 - headingHeight - 100
        chart.data = [[x[1] for x in data]]
        chart.categoryAxis.categoryNames = [str(x[0]) for x in data]
        chart.bars[0].fillColor = colors.black
        chart.categoryAxis.style = 'stacked'

        # Add the bar chart to the drawing
        drawing.add(chart)

        # Draw the drawing on the canvas
        drawing.wrapOn(
            canv=self.canvas,
            aW=self.w - self.margin * 4,
            aH=chart.height
        )

        drawing.drawOn(
            canvas=self.canvas,
            x=self.margin,
            y=self.margin * 2
        )

    def addLineChart(self, profiles: list, y: int) -> None:
        # Add a heading 2
        headingHeight = self.addHeading2(
            text="Figure 1: Share price over the last 10 years.",
            x=self.margin,
            y=y - 40
        )

        # Add helptext
        self.addHelpText(
            text="(%) Return Plotted along the Y-axis.",
            y=y - headingHeight - 50
        )

        # Create a bar chart
        chart = HorizontalLineChart()
        chart.width = self.w - self.margin * 2.6
        chart.height = y - self.margin * 2 - headingHeight - 100

        chart.data = [profile.get('data', None) for profile in profiles]

        for i, profile in enumerate(profiles):
            chart.lines[i].strokeColor = HexColor(profile['color'])

        chart.fillColor = HexColor("#f5f5f5")
        chart.valueAxis.labels.fontName = 'Consola'
        chart.categoryAxis.visible = False

        # Create a ReportLab Drawing object
        drawing = Drawing(
            width=self.w - self.margin * 2,
            height=200
        )

        # Add the bar chart to the drawing
        drawing.add(chart)

        # Draw the drawing on the canvas
        drawing.wrapOn(
            canv=self.canvas,
            aW=self.w - self.margin * 6,
            aH=chart.height
        )

        drawing.drawOn(
            canvas=self.canvas,
            x=32,
            y=self.margin * 2
        )

        self.style.fontSize = 10
        self.style.textColor = HexColor("#000000")

        for i, profile in enumerate(profiles): 
            # Draw labels with colored circles on the line chart
            self.canvas.setStrokeColor(HexColor(profile['color']))
            p = Paragraph(profile['name'], style=self.style)
            p.wrapOn(self.canvas, self.w, self.h)
            p.drawOn(self.canvas, self.margin + 42, y -
                    self.margin * 2 - headingHeight - 48 - i * 17)

            self.canvas.setFillColor(HexColor(profile['color']))
            self.canvas.circle(self.margin + 32, y - self.margin *
                            2 - headingHeight - 40 - i * 17, 3, stroke=1, fill=1)

    def save(self) -> None:
        self.canvas.save()
