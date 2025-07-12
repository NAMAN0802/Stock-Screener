<!-- # Project Overview and flow

1. Download data from yfinance or web scrapping using beautifulsoup3
2. Store the data in Pandas dataframe
3. Clean the data, remove NaN, inf and -inf from data
4. Fundamental Analysis like P/E, Equity/Debt,etc.
5. Select the Stocks based on strong Fundamental Analysis
5. Technical Anlysis using different indicators like EMA, SMA, MACD, Super Trend, etc. on selected Stocks
6. Visualize the data 
7. Optimise the code
8. Deploy the project on frontend either using flask or Django (To Be Think..)

## 1. Downloading the data using yfinance

1. Learn yfinance
2. Get the stock symbols
3. fetch the data from yfinance
4. Store it in .csv files to not download again and again when code runs
5. Load those .csv in data frames -->

# Project Overview and Flow

## Data Gathering using API and Scraping
1. Download tick data from yfinance and store that in csv files.
2. Scrape fundamental data from www.screener.in using Scrapy and Selenium. 
3. To prevent IP blocking uses header rotation and delays.
4. Store the Raw scraped data in csv files.
5. Scraped data in the following format
    - summary
    - peer comparsion
    - profit loss
    - balance sheet
    - cash flow
    - quaterly results
    - ratios
    - shareholing patterns 

## Data Pipeline to Clean and Store data
1. 