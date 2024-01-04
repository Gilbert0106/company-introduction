import sys
from datetime import date
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
import requests
import yfinance as yf
import os.path



def main():
    # Check for correct usage of program
    if not len(sys.argv) == 2:
        sys.exit("Usage: python main.py [TICKER SYMBOL]")

    ticker = sys.argv[1]

    if len(ticker) < 2 or len(ticker) > 5:
        sys.exit("A valid ticker must be between 2 and 5 characters long.")

    # Check if user connected to internet
    if not internet_connection():
        sys.exit("Make sure you are connected to the internet.")

    # Check if ticker is a valid symbol by fetching data from API
    company = yf.Ticker(ticker)

    try:
        info = company.info
    except:
         sys.exit(ticker + " does not seem to be a valid ticker.")

    # Get date
    today = date.today()

    # Get width and height
    w, h = A4

    # Filename
    filename = "reports/" + ticker + "-" + today.strftime("%d%m%y") + ".pdf"

    # Check if file exists
    if os.path.isfile(filename): 
        sys.exit("A report for this ticker has already been generated today")

    # Start painting canvas
    canvas = Canvas(filename, pagesize=A4)
    canvas.drawString(72, h - 50, info['shortName'])

    # Save pdf
    canvas.save()


def internet_connection():
    try:
        requests.get("https://google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


# Call main()
if __name__ == "__main__":
    main()
