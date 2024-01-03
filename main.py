import sys
from datetime import date
from reportlab.pdfgen.canvas import Canvas


def main():
    if not len(sys.argv) == 2:
        sys.exit("Usage: python main.py [TICKER SYMBOL]")

    ticker = sys.argv[1]
    
    if len(ticker) < 2 or len(ticker) > 5:
        sys.exit("A valid ticker must be between 2 and 5 characters long.")

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
