import os.path
from datetime import date
from typing import Union

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart

from source.companyApi import CompanyApi


class Report(object):

    WIDTH, HEIGHT = A4

    TICKERS_TO_COMPARE = [
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

    FONT = {
        'name': 'Consola',
        'path': r"resources/fonts/CONSOLA.TTF"
    }

    IMAGE_PATH = "resources/images/clover.png"

    TOTAL_PAGE_COUNT = 2

    def __init__(self, company: CompanyApi, path: str) -> None:
        self.company = company
        self.path = path

        try:
            self.style = self.create_style(
                fontName=self.FONT['name'],
                fontPath=self.FONT['path']
            )
        except Exception as e:
            raise Exception(e)

        self.new_page()
        self.y = self.add_business_summary(self.y)
        self.y = self.add_box_column(
            data=self.company.get_introductory_metrics(),
            y=self.y
        )
        self.add_line_chart(
            profiles=self.company.get_historical_price_data(
                tickers_to_compare=self.TICKERS_TO_COMPARE
            ),
            y=self.y
        )

        self.new_page()

        self.y = self.add_vertical_bar_chart(
            data=self.company.get_revenue_and_earnings_data_for_bar_chart(),
            heading="Figure 2: Revenue and earnings per year.",
            help_text="Total revenue and net income per year ($ M.)",
            y=self.y
        )

        self.y = self.add_box_column(
            data=self.company.get_earnings_and_revenue_cagr(),
            y=self.y
        )

    def create_style(self, fontName: str, fontPath: str) -> list:
        if not os.path.isfile(path=fontPath):
            raise Exception("The font can not be loaded from: " + fontPath)

        self.margin = 32

        # Register font
        pdfmetrics.registerFont(
            TTFont(name=fontName, filename=fontPath)
        )

        # Set style sheet
        style = getSampleStyleSheet()['Normal']
        style.fontName = fontName
        style.leading = 15
        return style

    def new_page(self) -> None:
        if not hasattr(self, 'canvas'):
            self.pagesCount = 1
            self.canvas = Canvas(self.path, pagesize=A4)
        else:
            self.canvas.showPage()
            self.pagesCount += 1

        self.add_header()
        self.add_footer()

        self.y = self.HEIGHT - 64

    def add_header(self) -> None:
        # Load and draw the icon
        self.canvas.drawImage(self.IMAGE_PATH, 32, self.HEIGHT - 34,
                              width=10, height=10, preserveAspectRatio=True, mask='auto')
        self.canvas.setStrokeColorRGB(0, 0, 0)
        self.canvas.setLineWidth(1)

        self.canvas.line(32, self.HEIGHT - 45,
                         self.WIDTH - 32, self.HEIGHT - 45)

        self.add_text(
            text=f'Company Introduction | \
                {date.today().strftime("%dth of %B %Y")}',
            size=7,
            x=48,
            y=self.HEIGHT - 25
        )

        self.add_text(
            text=f'Page {self.pagesCount} of {self.TOTAL_PAGE_COUNT}.',
            size=7,
            x=-32,
            y=self.HEIGHT - 25,
            alignment=2
        )

    def add_footer(self) -> None:
        self.canvas.setStrokeColorRGB(0, 0, 0)
        self.canvas.setLineWidth(1)

        self.canvas.line(32, 45, self.WIDTH - 32, 46)

        self.add_text(
            text="https://github.com/Gilbert0106/company-introduction",
            size=7,
            color="#666666",
            x=-32,
            y=32.5,
            aW=self.WIDTH,
            alignment=2
        )

        self.add_text(
            text=f'© Company Introduction \
            {date.today().year}, Authored by Simon',
            size=7,
            x=32,
            y=32,
        )

    def add_heading_1(self, text: str, y: int, x: int = None) -> int:
        if x is None:
            x = self.margin

        return self.add_text(text=text, size=20, x=x, y=y)

    def add_heading_2(self, text: str, y: int, x: int = None) -> int:
        if x is None:
            x = self.margin

        return self.add_text(text=text, size=16, x=x, y=y)

    def add_paragraph(self, text: str, y: int, x: int = None) -> int:
        if x is None:
            x = self.margin

        return self.add_text(text=text, size=9, x=x, y=y)

    def add_help_text(self, text: str, y: int, x: int = None) -> int:
        if x is None:
            x = self.margin

        return self.add_text(text=text, size=9, color="#666666", x=x, y=y)

    def add_text(self, x: int, y: int, text: str, size: int, color: str = None, aW: int = None, aH: int = None, alignment: int = 0) -> Paragraph:
        if color is None:
            color = "#000000"
        if aW is None:
            aW = self.WIDTH - x - self.margin
        if aH is None:
            aH = self.HEIGHT

        self.style.fontSize = size
        self.style.textColor = HexColor(color)
        self.style.alignment = alignment
        p = Paragraph(text, style=self.style)
        p.wrapOn(self.canvas, aW, aH)
        p.drawOn(self.canvas, x, y - p.height)

        return p.height

    def add_business_summary(self, y: int) -> int:
        heading_height = self.add_heading_1(
            text="%s (%s)" % (self.company.get_name(),
                              self.company.get_symbol()),
            y=y
        )

        return y - self.add_paragraph(self.company.get_summary(), y=y - heading_height - 20) - heading_height - 20

    def add_box_column(self, data: list, y: int, height=60, spacing_between_boxes=10) -> int:

        column_width = self.WIDTH - 2 * self.margin
        box_width = (
            column_width - spacing_between_boxes * (len(data) - 1)
        ) / len(data)

        y = y - height - spacing_between_boxes * 2
        x = self.margin

        for item in data:
            self.draw_box(
                heading=item['value'],
                subtext=item['description'],
                x=x,
                y=y,
                height=height,
                width=box_width
            )
            x += spacing_between_boxes + box_width

        return y

    def draw_box(self, heading: str, subtext: str, x: int, y: int, width: int, height: int) -> None:
        self.canvas.setStrokeColor(HexColor("#ffffff"))
        self.canvas.setFillColor(HexColor("#f5f5f5"))

        self.canvas.rect(
            x=x,
            y=y,
            width=width,
            height=height,
            fill=True
        )

        self.add_text(
            x=x + 10,
            y=y + height - 15,
            text=heading,
            size=12
        )

        self.add_text(
            x=x + 10,
            y=y + 20,
            text=subtext,
            size=5,
            aW=width - 20
        )

    def add_vertical_bar_chart(self, data: list, heading: str, help_text: str, y: int, chart_height: int = 200) -> None:
        chart = VerticalBarChart()
        chart.strokeColor = colors.white
        chart.width = self.WIDTH - self.margin * 2.6
        chart.height = chart_height
        chart.data = data['values']

        chart.bars[0].fillColor = colors.black
        chart.bars[0].strokeColor = None
        chart.bars[1].fillColor = colors.grey
        chart.bars[1].strokeColor = None
        chart.fillColor = HexColor("#f5f5f5")
        chart.categoryAxis.categoryNames = data['category_names']
        chart.categoryAxis.labels.fontName = 'Consola'

        chart.valueAxis.labels.fontName = 'Consola'
        chart.valueAxis.labels.fontSize = 8
        chart.valueAxis.valueMin = min(min(*data['values'])) * 1.1
        chart.valueAxis.valueMax = max(max(*data['values'])) * 1.1

        return self.draw_chart(
            heading=heading,
            help_text=help_text,
            chart=chart,
            y=y
        )

    def add_line_chart(self, profiles: list, y: int) -> None:
        # Add a heading 2
        headingHeight = self.add_heading_2(
            text="Figure 1: Share price over the last 10 years.",
            x=self.margin,
            y=y - 20
        )

        # Add helptext
        self.add_help_text(
            text="(%) Return Plotted along the Y-axis.",
            y=y - headingHeight - 30
        )

        # Create a line chart
        chart = HorizontalLineChart()
        chart.width = self.WIDTH - self.margin * 2.6
        chart.height = y - self.margin * 2 - headingHeight - 70
        chart.fillColor = HexColor("#f5f5f5")
        chart.data = [profile.get('data', None) for profile in profiles]

        for i, profile in enumerate(profiles):
            chart.lines[i].strokeColor = HexColor(profile['color'])
            if i:
                chart.lines[i].strokeDashArray = (4, 2)

        chart.valueAxis.labels.fontName = 'Consola'
        chart.valueAxis.valueMax = max(
            max(profile.get('data', None)) for profile in profiles) * 1.05
        chart.categoryAxis.visible = False

        # Create a ReportLab Drawing object
        drawing = Drawing(
            width=self.WIDTH - self.margin * 2,
            height=200
        )

        # Add the bar chart to the drawing
        drawing.add(chart)

        # Draw the drawing on the canvas
        drawing.wrapOn(
            canv=self.canvas,
            aW=self.WIDTH - self.margin * 6,
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
            p.wrapOn(self.canvas, self.WIDTH, self.HEIGHT)
            p.drawOn(self.canvas,
                     self.margin + 42,
                     y - self.margin * 2 - headingHeight - 20 - i * 17
                     )

            self.canvas.setFillColor(HexColor(profile['color']))
            self.canvas.circle(
                self.margin + 32,
                y - self.margin * 2 - headingHeight - 12 - i * 17, 3,
                stroke=1,
                fill=1
            )

    def draw_chart(self, heading: str, help_text: str, chart: Union[HorizontalLineChart, VerticalBarChart], y: int) -> None:

        heading_height = self.add_heading_2(
            text=heading,
            x=self.margin,
            y=y - 20
        )

        self.add_help_text(
            text=help_text,
            y=y - heading_height - 30
        )

        drawing = Drawing(
            width=self.WIDTH - self.margin * 2,
            height=chart.height
        )

        drawing.add(chart)

        drawing.wrapOn(
            canv=self.canvas,
            aW=self.WIDTH - self.margin * 6,
            aH=chart.height
        )

        drawing.drawOn(
            canvas=self.canvas,
            x=32,
            y=self.y - chart.height - heading_height - 70
        )

        return self.y - chart.height - heading_height - 70

    def save(self) -> None:
        self.canvas.save()
