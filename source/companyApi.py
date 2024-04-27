import os
import io
import yfinance as yf
import requests
from typing import Optional
from datetime import datetime, timedelta
from alpha_vantage.timeseries import TimeSeries


class CompanyApi(object):
    ticker: str
    
    exchange: str
    
    currency: str
    
    CURRENCY_SYMBOLS = {
        'USD': '$',
        'EUR': '€',
        'YEN': '¥'
    }

    def __init__(self, ticker: str, exchange: str) -> None:
        self.ticker = ticker
        self.exchange = exchange
        self.logo_url = None

        try:
            self.set_yfinance_handle()
            self.set_alpha_vantage_handle()
            self.set_currency()
        except Exception as e:
            raise Exception(str(e))

    def set_yfinance_handle(self) -> None:
        try:
            self.yfinance_handle = yf.Ticker(self.ticker)
            self.info = self.yfinance_handle.info
            if self.info['quoteType'] != 'EQUITY':
                raise Exception(
                    self.ticker + " does not seem to be a valid company stock ticker.")
        except:
            raise Exception(
                f'"{self.ticker}", does not seem to be a valid ticker.')

    def set_alpha_vantage_handle(self) -> None:
        try:
            self.alpha_vantage_handle = TimeSeries(
                key=os.environ.get("ALPHA_VANTAGE_API_KEY"))
            self.income_statements = self.get_income_statements()
            self.cash_flow_statements = self.get_cash_flow_statements()
        except Exception as e:
            raise Exception(
                f"Failed to initialize Alpha Vantage API with the provided key. Error: {str(e)}")

    def get_logo(self) -> Optional[io.BytesIO]:
        response = requests.get(f'https://eodhd.com/img/logos/{self.exchange}/{self.ticker.lower()}.png')

        if response.status_code == 404: 
            response = requests.get(f'https://eodhd.com/img/logos/{self.exchange}/{self.ticker}.png')
    
        temp_path = "resources/temp/company-logo.png"
        
        if response.status_code == 200:
            with open(temp_path, "wb") as f:
                f.write(response.content)
            return temp_path


        print(f'Could not find an image for {self.ticker}, proceeding without it.')
        return None

    def set_currency(self) -> None:

        if not 'currency' in self.info.keys():
            raise Exception(f'Could not retireve all necessary data for ticker symbol: \
                 "{self.get_symbol()}", are there any other ticker symbols that represent this company?')
        elif self.info['currency'] in self.CURRENCY_SYMBOLS.keys():
            self.currency = self.CURRENCY_SYMBOLS[self.info['currency']]
        else:
            self.currency = self.info['currency']

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

    @staticmethod
    def format_percentage(number: int) -> str:
        return f'{round(number * 100, 2)} %'

    def format_amount(self, number: int) -> str:
        millnames = ['', 'K.', 'M.', 'B.', 'T.']
        for i in range(0, 5):
            if number < 1000 or i == 4:
                return f'{self.currency}{round(number, 2)} {millnames[i]}'
            else:
                number /= 1000

    @staticmethod
    def calculate_cagr(annualReports: dict, num_years: int, key: str) -> float:
        if len(annualReports) < num_years:
            raise Exception(
                "Not enough historical data to accurately value the company."
            )

        ending_value = float(annualReports[0][key])
        beginning_value = float(annualReports[num_years - 1][key])
        sign = 1 if ending_value >= beginning_value else -1

        return sign * abs((ending_value / beginning_value) ** (1 / num_years) - 1)

    def get_introductory_metrics_for_box_column(self) -> list:
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

    def get_revenue_and_earnings_data_for_box_column(self) -> list:
        return [
            {
                'value': self.format_percentage(self.calculate_cagr(self.income_statements, 3, "totalRevenue")),
                'description': '3 year total revenue CAGR.'
            },
            {
                'value': self.format_percentage(self.calculate_cagr(self.income_statements, 3, "netIncome")),
                'description': '3 year net income CAGR.'
            },
            {
                'value': self.format_percentage(self.calculate_cagr(self.income_statements, min(10, len(self.income_statements)), "totalRevenue")),
                'description': '10 year total revenue CAGR.'
            },
            {
                'value': self.format_percentage(self.calculate_cagr(self.income_statements, min(10, len(self.income_statements)), "netIncome")),
                'description': '10 year net income CAGR.'
            },
            {
                'value': self.format_percentage(self.calculate_cagr(self.income_statements, min(10, len(self.income_statements)), "netIncomeMargin")),
                'description': '10 year income margin CAGR.'
            }
        ]

    def get_operating_cash_flow_and_free_cash_flow_data_for_box_column(self) -> list:
        return [
            {
                'value': self.format_percentage(self.calculate_cagr(self.cash_flow_statements, 3, "operatingCashflow")),
                'description': '3 year OCF CAGR.'
            },
            {
                'value': self.format_percentage(self.calculate_cagr(self.cash_flow_statements, 3, "freeCashFlowEstimate")),
                'description': '3 year FCF CAGR.'
            },
            {
                'value': self.format_percentage(self.calculate_cagr(self.cash_flow_statements, min(10, len(self.cash_flow_statements)), "operatingCashflow")),
                'description': '10 year OCF CAGR.'
            },
            {
                'value': self.format_percentage(self.calculate_cagr(self.cash_flow_statements, min(10, len(self.cash_flow_statements)), "freeCashFlowEstimate")),
                'description': '10 year FCF CAGR.'
            },
        ]

    def get_historical_price_data_for_line_chart(self, tickers_to_compare: list, start_date: str = None) -> dict:

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

    def get_revenue_and_earnings_data_for_bar_chart(self) -> dict:

        data = {"category_names": [], "values": [[], []]}

        for statements in self.income_statements[:10]:
            data['category_names'].insert(0, str(datetime.strptime(
                statements['fiscalDateEnding'], '%Y-%m-%d').year))
            data['values'][0].insert(
                0, float(statements['totalRevenue']) / 1000000)
            data['values'][1].insert(
                0, float(statements['netIncome']) / 1000000)

        return data

    def get_cash_flow_data_for_bar_chart(self) -> dict:

        data = {"category_names": [], "values": [[], []]}

        for statements in self.cash_flow_statements[:10]:
            data['category_names'].insert(0, str(datetime.strptime(
                statements['fiscalDateEnding'], '%Y-%m-%d').year))
            data['values'][0].insert(
                0, float(statements['operatingCashflow']) / 1000000)
            data['values'][1].insert(
                0, float(statements['freeCashFlowEstimate']) / 1000000)

        return data

    def get_income_statements(self) -> dict:
        result = self.fetch("INCOME_STATEMENT")

        if not 'annualReports' in result:
            raise Exception(result["Information"])

        for annual_report in result['annualReports']:
            annual_report["netIncomeMargin"] = float(
                annual_report["netIncome"]) / float(annual_report["totalRevenue"])

        return result['annualReports']

    def get_cash_flow_statements(self) -> dict:
        result = self.fetch("CASH_FLOW")

        if not 'annualReports' in result:
            raise Exception(result["Information"])

        for annual_report in result['annualReports']:
            # Calculate Free Cash Flow (FCF) estimate
            annual_report["freeCashFlowEstimate"] = float(annual_report["operatingCashflow"]) - float(
                annual_report.get("depreciationDepletionAndAmortization", 0))

        return result['annualReports']

    def fetch(self, function) -> dict:
        return requests.get(f'https://www.alphavantage.co/query?function={function}&symbol={self.ticker}&apikey={os.environ.get("ALPHA_VANTAGE_API_KEY")}').json()
