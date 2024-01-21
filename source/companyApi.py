import yfinance as yf
from datetime import datetime, timedelta


class CompanyApi(object):
    CURRENCY_SYMBOLS = {
        'USD': '$',
        'EUR': '€',
        'YEN': '¥'
    }

    def __init__(self, ticker: str) -> None:
        try:
            self.handle = yf.Ticker(ticker)
            self.info = self.handle.info
        except:
            raise Exception(ticker + " does not seem to be a valid ticker.")

        if self.info['quoteType'] != 'EQUITY':
            raise Exception(
                ticker + " does not seem to be a valid company stock ticker.")

        self.currency = self.get_currency()

    def get_currency(self) -> str:

        if not 'currency' in self.info.keys():
            raise Exception(f'Could not retireve all necessary data for ticker symbol: \
                 "{self.get_symbol()}", are there any other ticker symbols that represent this company?')
        elif self.info['currency'] in self.CURRENCY_SYMBOLS.keys():
            return self.CURRENCY_SYMBOLS[self.info['currency']]
        else:
            return self.info['currency']

    def get_name(self) -> str:
        return self.info['shortName']

    def get_symbol(self) -> str:
        return self.info['symbol']

    def get_summary(self) -> str:
        return str(self.info['longBusinessSummary'])

    def get_pe(self) -> str:
        if 'trailingPE' in self.info:
            return str(round(self.info['trailingPE'], 2))
        else:
            return 'N/A'

    def format_percentage(self, number: int) -> str:
        return f'{round(number * 100, 2)} %'

    def format_amount(self, number: int) -> str:
        millnames = ['', 'K.', 'M.', 'B.', 'T.']
        for i in range(0, 5):
            if number < 1000 or i == 4:
                return f'{self.currency}{round(number, 2)} {millnames[i]}'
            else:
                number /= 1000

    def get_introductory_metrics(self) -> list:
        return [
            {
                'value': self.format_amount(self.info['marketCap']),
                'description': 'Market capitalization.'
            },
            {
                'value': self.format_amount(self.info['totalRevenue']),
                'description': 'Total annual revenue.'
            },
            {
                'value': self.format_percentage(self.info["ebitdaMargins"]),
                'description': 'EBITDA / total revenue.'
            },
            {
                'value': self.get_pe(),
                'description': 'Trailing Price/Earnings.'
            },
            {
                'value': self.format_percentage(self.info["trailingAnnualDividendYield"]),
                'description': 'Dividend yield.'
            }
        ]

    def get_historical_price_data(self, tickers: list, start_date: str = None) -> dict:

        if start_date == None:
            start_date = (datetime.now() - timedelta(days=10 * 365)
                          ).strftime('%Y-%m-%d')

        tickers.insert(0, {
            'ticker': self.get_symbol(),
            'color': '#FF0000',
            'name': self.get_name(),
        })

        for ticker in tickers:
            # Download ticker data
            ticker_data = yf.download(
                ticker['ticker'], start=start_date, interval="1mo")['Close']

            # Calulate the factor to apply on all values
            x = 100 / ticker_data.iloc[0]

            # Format data and put it in dict
            ticker['data'] = [(date.strftime('%Y-%m'), closing_price * x - 100)[1]
                              for date, closing_price in zip(ticker_data.index, ticker_data)]

        return tickers
