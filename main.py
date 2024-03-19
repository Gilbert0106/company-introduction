import sys
import os.path
import argparse
import requests
from datetime import date
from dotenv import load_dotenv
from typing import Optional, Dict, Any

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

    selected_option = search_ticker_and_present_options("MSFT")
        
    try:
        # Initalize a new CompanyApi and Report
        company = CompanyApi(ticker=selected_option['Code'])
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


def search_ticker_and_present_options(ticker_symbol=str)-> Optional[Dict[str, int]]:
    
    options = requests.get(f'https://eodhd.com/api/search/{ticker_symbol}?type=stock&api_token={os.environ.get("EODHD_API_KEY")}&fmt=json').json()

    if len(options) == 1: 
        return options[0]
    
    print("Please choose from the following options:")
    
    for index, option in enumerate(options, start=1):
        print(f"{index}. {option['Name']} ({option['Code']}) - Country: {option['Country']}, Exchange: {option['Exchange']}")

    choice = input("Enter the number corresponding to your choice: ")

    try:
        choice_index = int(choice) - 1
        if 0 <= choice_index < len(options):
            return options[choice_index]
        else:
            print("Invalid choice. Please enter a number within the range.")
            return None
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None
      
  
if __name__ == "__main__":
    main()
