import sys
import os.path
import argparse
import requests
from datetime import date
from dotenv import load_dotenv

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
    filepath = f'reports/{ args.ticker_symbol }-{date.today().strftime("%y%m%d")}.pdf'
    load_dotenv()

    # Make sure correct usage of program
    if len(args.ticker_symbol) < 3 or len(args.ticker_symbol) > 10:
        sys.exit("A valid ticker must be between 3 and 9 characters long.")
    elif not check_internet_connection():
        sys.exit("Make sure you are connected to the internet.")
    elif os.path.isfile(path=filepath) and not args.overwrite:
        sys.exit(f'A report for ticker {args.ticker_symbol} has already been generated today. If you would like to overwrite the previous version you may run the program with --overwrite.')

    try:
        # Initalize a new CompanyApi and Report
        company = CompanyApi(ticker=args.ticker_symbol)
        report = Report(company=company, path=filepath)
    except Exception as e:
        sys.exit(e)

    # Save report
    report.save()


def check_internet_connection():
    try:
        requests.get("https://google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


# Call main()
if __name__ == "__main__":
    main()
