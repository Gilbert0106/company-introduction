import sys

def main():
    if not len(sys.argv) == 2:
        sys.exit("Usage: python main.py TICKER")
    
    ticker = sys.argv[1]
    if len(ticker) < 2 or len(ticker) > 5: 
        sys.exit("A valid ticker must be between 2 and 5 characters long.")

# Run Main function
if __name__ == "__main__":
    main()
