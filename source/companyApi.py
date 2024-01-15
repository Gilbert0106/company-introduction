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

    def getPE(self) -> str:
        if 'trailingPE' in self.info:
            return str(round(self.info['trailingPE'], 2))
        else:
            return 'N/A'

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
                'value': self.getPE(),
                'description': 'Trailing Price/Earnings.'
            },
            {
                'value': self.formatPercentage(self.info["trailingAnnualDividendYield"]),
                'description': 'Dividend yield.'
            }
        ]

    def getHistoricalStockData(self) -> list:
        # Get historical data using the history function
        data = self.handle.history(period="max", interval="3mo")['Close'].items()

        # Get comparable index during same time? Like NASDAQ or S&P 500

        return [
            (date.strftime('%Y-%m'), closing_price) if i == 1 or i % 25 == 0 else ('', closing_price)
            for i, (date, closing_price) in enumerate(data, 1)
        ]
