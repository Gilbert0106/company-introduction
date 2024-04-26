# Company Introduction
A dockerized Python CLI program that generates a report of a publically traded company based on ticker symbol.

# Prerequisites
1. [Install Docker](https://docs.docker.com/get-docker/)
2. Clone this repository
3. Generate an API key for Alpha Vantage

## Environment Configuration

This project depends upon the Alpha Vantage API and EODHD API. So to use this application you are required to configure these two api keys.

1. **Get a free Alpha Vantage API Key:**
   - If you don't have an Alpha Vantage API key, you can generate a free one from [https://www.alphavantage.co/support/](https://www.alphavantage.co/support/).<br>

2. **Get a free EODHD API Key:**
   - If you don't have an a EODHD API key, you can generate a free one by signing up at [https://eodhd.com/register](https://eodhd.com/register).

3. **Copy the Example Environment File:**
   - In the project root directory, you will find an example environment file named `.env.example`.
   - Copy this file and create a new file named `.env` in the same directory.

4. **Replace the Placeholder with Your API Keys:**
   - Open the `.env` file in a text editor.
   - Locate the line `ALPHA_VANTAGE_API_KEY=YOUR_API_KEY_HERE`.
   - Replace `YOUR_API_KEY_HERE` with your actual Alpha Vantage API key.
   - Locate the line `EODHD_API_KEY=YOUR_API_KEY_HERE`.
   - Replace `YOUR_API_KEY_HERE` with your actual EODHD API key.

5. **Save the Changes:**
   - Save the changes to the `.env` file.

# A) Starting the container using docker-compose
In order to use the application you will need to build an image and start a container of it.
1. You will first need to cd into the directory after cloning it `company-introduction`

```
cd company-introduction
```

2. Run the command below to build to build an image and start a container using docker-compose

```
sudo docker-compose run company_introduction
```


# B) Building the image and running the container

In order to use the application you will need to build an image and start a container of it.
1. You will first need to cd into the directory after cloning it `company-introduction`

```
cd company-introduction
```

2. Run the command below to build an image called `company_introduction_image` based on the `Dockerfile` that can be located in the root of the project

```
docker build -t company_introduction_image --rm .
```

3. Run the command below to start a container called `company-introduction` using the `company_introduction_image`. Replace /path/on/host with the absolute path on your host machine where you want to store the generated reports.

```
docker run --name company_introduction_container --rm -v /path/on/host:/usr/app/src/reports -it company_introduction_image
```

Note: If the path contains spaces, you may need to use quotes around the path, like this:

```
"/path/with spaces/on/host":"/usr/app/src/reports"
```

# Usage

In order to generate a report for the company run the below command while attached to the container. Company query is the search term you want the program to use while looking for the stock.

```
generate-report [COMPANY QUERY]
```

Then choose from the list of options which company to generate the report for.

```
Please choose from the following options:
1. Option 1 - Country: USA, Exchange: US
2. Option 2 - Country: USA, Exchange: US
3. Option 3 - Country: USA, Exchange: US

Enter the number corresponding to your choice:
```

**Example** 
Generating report for Netflix (Ticker symbol NFLX us exchange)

```
generate-report Netflix
```

```
Please choose from the following options:
1. Netflix Inc (NFLX) - Country: USA, Exchange: US
2. Netflix Inc. (0QYI) - Country: UK, Exchange: LSE
3. Netflix Inc (NFC) - Country: Germany, Exchange: XETRA
4. Netflix Inc CDR (NFLX) - Country: Canada, Exchange: NEO
5. Netflix Inc (NFLX34) - Country: Brazil, Exchange: SA
6. Netflix Inc (NFLX) - Country: Mexico, Exchange: MX
7. Netflix Inc (NFC) - Country: Germany, Exchange: F
8. Netflix Inc (NFC) - Country: Germany, Exchange: STU
9. Netflix Inc (NFC) - Country: Germany, Exchange: DU
10. Netflix Inc (NFC) - Country: Germany, Exchange: BE
11. Netflix Inc (NFC) - Country: Germany, Exchange: MU
12. NETFLIX INC. CDR (NFC1) - Country: Germany, Exchange: F

Enter the number corresponding to your choice: 1
```

If you would like to generate a new report on the same company on the same day you will have to use the flag --overwrite, see below for example

```
generate-report Netflix --overwrite
```

To get some information on the arguments available please use -h or --help

```
generate-report -h
```
