# import pandas as pd
# import numpy as np
# from yahoo_finance_data import get_tick_data_using_yfinance 
# import os

# if __name__=="__main__":

#     tickers=pd.read_csv("Ticker_List_NSE_India.csv")
#     tickers.columns = tickers.columns.str.strip()
#     # tickers.drop(columns=["SYMBOL","NAME OF COMPANY","SERIES","DATE OF LISTING","PAID UP VALUE","MARKET LOT","ISIN NUMBER","FACE VALUE","Unnamed: 8","Yahoo_Equivalent_Code"],inplace=True)
#     ticker_name=tickers["YahooEquiv"].tolist()
#     # print(ticker_name)
#     for ticker in ticker_name:
#         filename=f"fundamental_data/{ticker.replace('.NS','')}.json"
#         if os.path.exists(filename):
#             print(f"Data for {ticker} already exists")
#         else:
#             get_tick_data_using_yfinance(ticker,filename)
            

import os,sys
import pandas as pd
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from glob import glob

# 🔧 Add the inner stock_scraper to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'stock_scraper'))

# ✅ Correct import now
from stock_scraper.spiders.stock_sprider import StockSpider
import stock_scraper.settings as spider_settings

# Required files (modify as needed)
REQUIRED_FILES = {
    'summary.csv', 'peer_comparison.csv', 'quarterly_results.csv',
    'profit_loss.csv', 'balance_sheet.csv', 'cash_flow.csv',
    'ratios.csv', 'shareholding.csv'
}

# def should_scrape(ticker):
#     folder = os.path.join("fundamental_data", ticker)
#     return not os.path.exists(folder) or len(os.listdir(folder)) < 8  # You define threshold

def should_scrape(ticker):
    """Returns True if ticker needs scraping (missing/incomplete data)"""
    # Find all matching ticker folders (5 levels deep)
    ticker_paths = glob(f"fundamental_data/*/*/*/*/{ticker}")
    
    # If no folder exists, needs scraping
    if not ticker_paths:
        return True
    
    # Check if any existing folder has all files
    for path in ticker_paths:
        if set(os.listdir(path)).issuperset(REQUIRED_FILES):
            return False
    
    # If we get here, data is incomplete
    return True

if __name__ == "__main__":
    ticker = pd.read_csv("D:\python project\data scraper\Ticker_List_NSE_India.csv")
    tickers = ticker["SYMBOL"].to_list()  # Extend this list as needed
    # tickers=['INFY','RELIANCE','TATAMOTORS','TCS','TATASTEEL','WIPRO','NESTLEIND']

    results = [ticker for ticker in tickers if should_scrape(ticker)]
    print("✅ Tickers to scrape:", len(results))
    if results:     
        settings=Settings()  
        for key in dir(spider_settings):
            if key.isupper():
                settings.set(key, getattr(spider_settings, key))
        print (settings.attributes.items())
        print("✅ Final middleware:", dict(settings.get("DOWNLOADER_MIDDLEWARES")))

        process = CrawlerProcess(settings)  
        full = not os.path.exists("fundamental_data")  # True if folder doesn't exist  
        url = f"https://www.screener.in/company/"
        process.crawl(StockSpider, base_url=url, tickers=results,full=full)  # passing args dynamically
        process.start()
    else:
        print("✅ All tickers already scraped.")
