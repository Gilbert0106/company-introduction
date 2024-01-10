import sys
import requests

from source.report import Report
from source.companyApi import CompanyApi


def main():
    # Make sure correct usage of program
    if not len(sys.argv) == 2:
        sys.exit("Usage: python main.py [TICKER SYMBOL]")
    elif len(sys.argv[1]) < 2 or len(sys.argv[1]) > 5:
        sys.exit("A valid ticker must be between 2 and 5 characters long.")
    elif not internet_connection():
        sys.exit("Make sure you are connected to the internet.")

    # Initalize a new CompanyApi and Report
    try:
        company = CompanyApi(ticker=sys.argv[1])
        report = Report(company=company)
    except Exception as e:
         sys.exit(e)
    
    # Save report
    report.save()

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
