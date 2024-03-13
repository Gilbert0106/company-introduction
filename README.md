# Company Introduction
A dockerized Python CLI program that generates a report of a publically traded company based on ticker symbol.

# Prerequisites
1. [Install Docker](https://docs.docker.com/get-docker/)
2. Clone this repository
3. Generate an API key for Alpha Vantage

## Environment Configuration

### Alpha Vantage API Key

This project depends upon the Alpha Vantage API. So to use this application you are required to configure your api key.

1. **Get a free Alpha Vantage API Key:**
   - If you don't have an Alpha Vantage API key, you can generate a free one from [https://www.alphavantage.co/support/](https://www.alphavantage.co/support/).

2. **Copy the Example Environment File:**
   - In the project root directory, you will find an example environment file named `.env.example`.
   - Copy this file and create a new file named `.env` in the same directory.

3. **Replace the Placeholder with Your API Key:**
   - Open the `.env` file in a text editor.
   - Locate the line `ALPHA_VANTAGE_API_KEY=YOUR_API_KEY_HERE`.
   - Replace `YOUR_API_KEY_HERE` with your actual Alpha Vantage API key.

4. **Save the Changes:**
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

In order to generate a report for the company run the below command while attached to the container

```
generate-report [TICKER SYMBOL]
```

**Example** 
Generating report for Netflix (Ticker symbol NFLX)

```
generate-report NFLX
```

If you would like to generate a new report on the same company on the same day you will have to use the flag --overwrite, see below for example

```
generate-report NFLX --overwrite
```

To get some information on the arguments available please use -h or --help

```
generate-report -h
```
