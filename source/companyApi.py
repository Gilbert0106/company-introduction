import yfinance as yf


class CompanyApi(object):
    def __init__(self, ticker: str) -> None:
        try:
            self.handle = yf.Ticker(ticker)
            self.info = self.handle.info
        except:
            raise Exception(ticker + " does not seem to be a valid ticker.")

        if self.info['quoteType'] != 'EQUITY':
            raise Exception(
                ticker + " does not seem to be a valid company stock ticker.")

        self.currency = self.getCurrency()

    def getCurrency(self) -> str:

        currencySymbol = {
            'USD': '$',
            'EUR': '€',
            'YEN': '¥'
        }

        if not 'currency' in self.info.keys():
            raise Exception(f'Could not retireve all necessary data for ticker symbol: \
                 "{self.getSymbol()}", are there any other ticker symbols that represent this company?')
        elif self.info['currency'] in currencySymbol.keys():
            return currencySymbol[self.info['currency']]
        else:
            return self.info['currency']

    def getName(self) -> str:
        return self.info['shortName']

    def getSymbol(self) -> str:
        return self.info['symbol']

    def getSummary(self) -> str:
        return str(self.info['longBusinessSummary'])

    def formatPercentage(self, number: int) -> str:
        return f'{round(number * 100, 2)} %'

    def formatAmount(self, number: int) -> str:
        millnames = ['', 'K.', 'M.', 'B.', 'T.']
        for i in range(0, 5):
            if number < 1000 or i == 4:
                return f'{self.currency}{round(number, 2)} {millnames[i]}'
            else:
                number /= 1000

    def getIntroductoryMetrics(self) -> list:
        return [
            {
                'value': self.formatAmount(self.info['marketCap']),
                'description': 'Market capitalization.'
            },
            {
                'value': self.formatAmount(self.info['totalRevenue']),
                'description': 'Total annual revenue.'
            },
            {
                'value': self.formatPercentage(self.info["ebitdaMargins"]),
                'description': 'EBITDA / total revenue.'
            },
            {
                'value': str(round(self.info['trailingPE'], 2)),
                'description': 'Trailing Price/Earnings.'
            },
            {
                'value': self.formatPercentage(self.info["trailingAnnualDividendYield"]),
                'description': 'Dividend yield.'
            }
        ]

    def getBarChartData(self) -> list:
        # Example data for the bar chart
        return [(1, 20), (2, 50), (3, 30), (4, 40), (5, 10)]
