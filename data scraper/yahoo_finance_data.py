import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

def get_tick_data_using_yfinance(ticker,filename):
    # data=yf.download(ticker,start="2023-01-01",end="2025-06-09",interval="1d",threads=True,group_by="ticker")
    # if not data.empty:
    #     os.makedirs(os.path.dirname(filename), exist_ok=True)
    #     data.to_csv(filename)
    # else:
    #     print(f"Data for {ticker} not found")
    data=yf.Ticker(ticker)
    json_data=json.dumps(data.info,indent=4)
    # print(json_data)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json_data)

# get_data_using_yfinance("RELIANCE.NS")