import yfinance as yf


class CompanyApi(object):
      def __init__(self, ticker):
        # Check if ticker is a valid symbol by fetching data from API
        try:
            self.info = yf.Ticker(ticker).info
        except:
            raise Exception(ticker + " does not seem to be a valid ticker.")