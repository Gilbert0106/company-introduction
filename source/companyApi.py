import yfinance as yf
from datetime import datetime, timedelta


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


        self.getHistoricalPriceData(
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


    def getHistoricalPriceData(self, tickers: list, start_date: str = None) -> dict:
        
        if start_date == None: 
            start_date = (datetime.now() - timedelta(days=10 * 365)).strftime('%Y-%m-%d')

        tickers.insert(0, {
            'ticker': self.getSymbol(), 
            'color': '#FF0000', 
            'name': self.getName(),
        })

        for ticker in tickers:
            # Download ticker data
            ticker_data = yf.download(ticker['ticker'], start=start_date, interval="1mo")['Close']

            # Calulate the factor to apply on all values
            x = 100 / ticker_data.iloc[0] 

            # Format data and put it in dict 
            ticker['data'] = [(date.strftime('%Y-%m'), closing_price * x - 100)[1] for date, closing_price in zip(ticker_data.index, ticker_data)]
   
        return tickers
