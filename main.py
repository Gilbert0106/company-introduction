import sys
from datetime import date
from reportlab.pdfgen.canvas import Canvas
import yfinance as yf



def main():
    if not len(sys.argv) == 2:
        sys.exit("Usage: python main.py [TICKER SYMBOL]")

    ticker = sys.argv[1]

    if len(ticker) < 2 or len(ticker) > 5:
        sys.exit("A valid ticker must be between 2 and 5 characters long.")

    # Check if ticker is a valid symbol by fetching data from API
    company = yf.Ticker(ticker)

    try:
        info = company.info
    except:
         sys.exit(ticker + " does not seem to be a valid ticker.")

    # Get date
    today = date.today()

    # Start painting canvas
    canvas = Canvas("reports/" + ticker + "-" + today.strftime("%d%m%y") + ".pdf")
    canvas.drawString(72, 72, "Hello, World!")

    # Save pdf
    canvas.save()


# Call main()
if __name__ == "__main__":
    main()
