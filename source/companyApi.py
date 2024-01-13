import yfinance as yf


class CompanyApi(object):
    def __init__(self, ticker: str) -> None:
        # Check if ticker is a valid symbol by fetching data from API
        try:
            self.handle = yf.Ticker(ticker)
            self.info = self.handle.info
        except:
            raise Exception(ticker + " does not seem to be a valid ticker.")

        if self.info['quoteType'] != 'EQUITY':
            raise Exception(
                ticker + " does not seem to be a valid company stock ticker.")

    def getName(self) -> str:
        return self.info['shortName']

    def getSymbol(self) -> str:
        return self.info['symbol']

    def getSummary(self) -> str:
        return str(self.info['longBusinessSummary'])

    # TODO: Create method to return a list of dicts with market cap, revenue, gross margin, P/E, dividend yield
    def getIntroductoryMetrics(self) -> list:
        return [
            {
                'value': '$3 000 B.',
                'description': 'Market capitalization.'
            },
            {
                'value': '$1 200 B.',
                'description': 'Revenue for previous year.'
            },
            {
                'value': '46.68 %',
                'description': 'Gross margin.'
            },
            {
                'value': '37.06',
                'description': 'Price/Earnings.'
            },
            {
                'value': '0.74 %',
                'description': 'Dividend yield.'
            }
        ]
