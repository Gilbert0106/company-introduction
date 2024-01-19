import sys
import argparse
import requests

from source.report import Report
from source.companyApi import CompanyApi


def main():
    # Create parser and add arguments
    parser = argparse.ArgumentParser(
        prog='Company Introduction',
        description='Provided a ticker symbol, the program will generate and save a PDF to your local computer',
    )

    parser.add_argument(
        "ticker_symbol",
        help="The unique ticker symbol of the company you want to create a report on"
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing report from today"
    )

    args = parser.parse_args()

    # Make sure correct usage of program
    if len(args.ticker_symbol) < 3 or len(args.ticker_symbol) > 10:
        sys.exit("A valid ticker must be between 2 and 10 characters long.")
    elif not check_internet_connection():
        sys.exit("Make sure you are connected to the internet.")

    # Initalize a new CompanyApi and Report
    try:
        company = CompanyApi(ticker=args.ticker_symbol)
        report = Report(company=company, overwrite=args.overwrite)
    except Exception as e:
        sys.exit(e)

    # Save report
    report.save()


def check_internet_connection():
    # Check for internet connection
    try:
        requests.get("https://google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


# Call main()
if __name__ == "__main__":
    main()
