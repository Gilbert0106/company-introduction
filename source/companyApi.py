import os
import yfinance as yf
import requests
from datetime import datetime, timedelta
from alpha_vantage.timeseries import TimeSeries


class CompanyApi(object):
    CURRENCY_SYMBOLS = {
        'USD': '$',
        'EUR': '€',
        'YEN': '¥'
    }

    def __init__(self, ticker: str) -> None:
        self.ticker = ticker

        try:
            self.yfinance_handle = yf.Ticker(self.ticker)
            self.info = self.yfinance_handle.info
        except:
            raise Exception(
                self.ticker + " does not seem to be a valid ticker.")

        try:
            self.alpha_vantage_handle = TimeSeries(
                key=os.environ.get("ALPHA_VANTAGE_API_KEY"))
            self.income_statements = self.get_income_statements()
        except Exception as e:
            raise Exception(
                f"Failed to initialize Alpha Vantage API with the provided key. Error: {str(e)}")

        if self.info['quoteType'] != 'EQUITY':
            raise Exception(
                self.ticker + " does not seem to be a valid company stock ticker.")

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

    def get_trailing_annual_dividend_yield(self) -> int:
        if 'trailingAnnualDividendYield' in self.info:
            return str(self.format_percentage(self.info['trailingAnnualDividendYield']))
        else:
            return '0.0 %'

    def format_percentage(self, number: int) -> str:
        return f'{round(number * 100, 2)} %'

    def format_amount(self, number: int) -> str:
        millnames = ['', 'K.', 'M.', 'B.', 'T.']
        for i in range(0, 5):
            if number < 1000 or i == 4:
                return f'{self.currency}{round(number, 2)} {millnames[i]}'
            else:
                number /= 1000

    def calculate_cagr(self, num_years: int, key: str):
        num_reports = len(self.income_statements)

        if num_reports < num_years:
            raise Exception("Not enough historical data to accurately value the company.")

        ending_value = float(self.income_statements[0][key])
        beginning_value = float(self.income_statements[num_years - 1][key])

        return (ending_value / beginning_value) ** (1 / num_years) - 1

    def get_introductory_metrics(self) -> list:
        return [
            {
                'value': self.format_amount(self.info['marketCap']),
                'description': 'Market Capitalization.'
            },
            {
                'value': self.format_amount(self.info['totalRevenue']),
                'description': 'Total Annual Revenue.'
            },
            {
                'value': self.format_percentage(self.info["ebitdaMargins"]),
                'description': 'EBITDA / Total Revenue.'
            },
            {
                'value': self.get_pe(),
                'description': 'Trailing Price / Earnings.'
            },
            {
                'value': self.get_trailing_annual_dividend_yield(),
                'description': 'Trailing Dividend Yield.'
            }
        ]

    def get_earnings_and_revenue_cagr(self) -> list:
        return [
            {
                'value': self.format_percentage(self.calculate_cagr(3, "totalRevenue")),
                'description': '3 year total revenue CAGR.'
            },
            {
                'value': self.format_percentage(self.calculate_cagr(3, "netIncome")),
                'description': '3 year net income CAGR.'
            },
            {
                'value': self.format_percentage(self.calculate_cagr(10, "totalRevenue")),
                'description': '10 year total revenue CAGR.'
            },
            {
                'value': self.format_percentage(self.calculate_cagr(10, "netIncome")),
                'description': '10 year net income CAGR.'
            },
            {
                'value': self.format_percentage(self.calculate_cagr(10, "netIncomeMargin")),
                'description': '10 year net income margin CAGR.'
            }
        ]

    def get_historical_price_data(self, tickers_to_compare: list, start_date: str = None) -> dict:

        if start_date == None:
            start_date = (datetime.now() - timedelta(days=10 * 365)
                          ).strftime('%Y-%m-%d')

        tickers_to_compare.insert(0, {
            'ticker': self.get_symbol(),
            'color': '#FF0000',
            'name': self.get_name(),
        })

        for ticker in tickers_to_compare:
            # Download ticker data
            ticker_data = yf.download(
                ticker['ticker'], start=start_date, interval="1mo")['Close']

            # Calculate the factor to apply on all values
            x = 100 / ticker_data.iloc[0]

            # Format data and put it in dict
            ticker['data'] = [(date.strftime('%Y-%m'), closing_price * x - 100)[1]
                              for date, closing_price in zip(ticker_data.index, ticker_data)]

        return tickers_to_compare

    def get_revenue_and_earnings_data_bar_chart(self) -> dict:

        data = {"years": [], "revenues": [], "earnings": []}

        for statements in self.income_statements[:10]:
            data['years'].insert(0, datetime.strptime(
                statements['fiscalDateEnding'], '%Y-%m-%d').year)
            data['revenues'].insert(
                0, float(statements['totalRevenue']) / 1000000)
            data['earnings'].insert(
                0, float(statements['netIncome']) / 1000000)

        return data

    def get_income_statements(self) -> dict:    
        result = self.fetch("INCOME_STATEMENT")

        if not 'annualReports' in result:
            raise Exception(result["Information"])
            
        for annual_report in result['annualReports']:
            annual_report["netIncomeMargin"] = (float(annual_report["netIncome"]) / float(annual_report["totalRevenue"]))
        
        return result['annualReports']

    def fetch(self, function) -> dict:
        return requests.get(f'https://www.alphavantage.co/query?function={function}&symbol={self.ticker}&apikey={os.environ.get("ALPHA_VANTAGE_API_KEY")}').json()
