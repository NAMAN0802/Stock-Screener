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
1. Read all csvs and store that in raw df
2. If it is summary csv then make it a series and based on the numerical columns, clean the data like convert the strings to integer and store that cleaned series in preprocessed_data_for_calc_and_detail dictionary with summary as column.
3. For all other dataframes in raw df like profit loss, cash flow, balance sheet and quarterly results, transpose the data so that all the raws which are date become column and all the columns which are parameters become rows. While doing this process, all the columns are cleans like removing extra spcaes, +, % from column name and remove dublicate columns.
4. In case of profit loss, all the columns after divident yields drops.
5. In case of quarterly results, last columns which is raw pdf drops.
6. After that all the data frames are stored in preprocessed_data_for_calc_and_detail dictionary with key as the name of the csv file.
7. preprocessed_data_for_calc_and_detail dictionary is then pased to function which calculate all the ratios and returned to pre computed fields.
