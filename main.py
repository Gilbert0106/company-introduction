import sys
import requests

from source.report import Report
from source.companyApi import CompanyApi


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

    # Initalize a new CompanyApi
    try:
        company = CompanyApi(ticker)
    except Exception as e:
         sys.exit(e)

    # Initialize a new report
    try:
        r = Report(ticker)
    except Exception as e:
         sys.exit(e)
    
    r.add_title(company.info['shortName'])
    r.add_business_summary(company.info['longBusinessSummary'])
    r.new_page()
    r.save()

# Check for internet connection
def internet_connection():
    try:
        requests.get("https://google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


# Call main()
if __name__ == "__main__":
    main()
