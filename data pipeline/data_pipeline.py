# data_pipeline.py

import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from database import Database
from models import Stocks, Ratios, ProfitLoss, Shareholding, CashFlow, BalanceSheet
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Aapke root directory ka path
RAW_DATA_ROOT_DIR = "Commodities"
PROCESSED_DATA_DIR = "processed_data"

def calculate_ratios(data: dict) -> dict:
    """
    Input data dictionary se saare pre-computed ratios calculate karta hai.
    """
    # Yeh ek placeholder hai. Yahan saare ratios ka calculation logic aayega.
    # Upar discuss kiye gaye TTM P/E, OCF Growth, P/S Ratio, etc. ka logic yahan likhenge.
    # Abhi ke liye, hum ek dummy value return kar rahe hain.
    
    # Example for TTM P/E:
    # quarterly_df = pd.DataFrame(data['quarterly_results'])
    # ttm_eps = quarterly_df['EPS'].tail(4).sum()
    # current_price = data['stock_info']['CMP Rs.']
    # data['stock_info']['ttm_pe_ratio'] = current_price / ttm_eps
    
    data['stock_info']['ttm_pe_ratio'] = 25.5
    data['stock_info']['operating_cash_flow_yoy'] = 10.2
    
    # Yahan baaki calculations add karenge
    
    return data['stock_info']


def process_stock_data(stock_path: str, stock_symbol: str, sector: str) -> dict:
    """
    Ek stock ke saare CSV files ko process karke uske liye data return karta hai.
    """
    if not os.path.exists(stock_path):
        logging.warning(f"Skipping {stock_symbol}: Stock data folder not found at {stock_path}.")
        return None, None

    logging.info(f"Processing data for stock: {stock_symbol} in sector: {sector}")
    
    # Files ko read karte hain
    try:
        summary_df = pd.read_csv(os.path.join(stock_path, "summary.csv"))
        profit_loss_df = pd.read_csv(os.path.join(stock_path, "profit_loss.csv"))
        balance_sheet_df = pd.read_csv(os.path.join(stock_path, "balance_sheet.csv"))
        cash_flow_df = pd.read_csv(os.path.join(stock_path, "cash_flow.csv"))
        quarterly_results_df = pd.read_csv(os.path.join(stock_path, "quarterly_results.csv"))
        ratios_df = pd.read_csv(os.path.join(stock_path, "ratios.csv"))
        shareholding_df = pd.read_csv(os.path.join(stock_path, "shareholding.csv"))
    except FileNotFoundError as e:
        logging.error(f"Error reading CSV files for {stock_symbol}: {e}")
        return None, None

    # Ab hum yahan par saare pre-computation aur data cleaning ka logic likhenge.
    # Data ko dictionaries mein convert karte hain
    processed_data = {
        "stock_info": summary_df.iloc[0].to_dict(),
        "profit_loss": profit_loss_df.to_dict('records'),
        "balance_sheet": balance_sheet_df.to_dict('records'),
        "cash_flow": cash_flow_df.to_dict('records'),
        "quarterly_results": quarterly_results_df.to_dict('records'),
        "ratios": ratios_df.to_dict('records'),
        "shareholding": shareholding_df.to_dict('records'),
    }

    # Yahan hum aapke TTM P/E aur OCF Growth jaise ratios ko calculate karenge
    # calculate_ratios function ko call karenge
    precomputed_fields = calculate_ratios(processed_data)
    precomputed_fields['sector'] = sector  # Sector ko bhi add karte hain
    precomputed_fields['symbol'] = stock_symbol
    
    return precomputed_fields, processed_data # Do values return karte hain

def main():
    """
    Main data pipeline function jo nested directories mein stocks ko process karta hai.
    """
    db_manager = Database()
    db_manager.create_tables()

    Session = sessionmaker(bind=db_manager.engine)
    
    # os.walk() ka use karke nested directories ko traverse karte hain
    for dirpath, dirnames, filenames in os.walk(RAW_DATA_ROOT_DIR):
        if 'balance_sheet.csv' in filenames:
            # Hum ek stock directory mein hain
            stock_path = dirpath
            stock_symbol = os.path.basename(stock_path)
            # Sector ka naam parent directory se nikalte hain
            sector = os.path.basename(os.path.dirname(stock_path))
            
            precomputed_data, detailed_data = process_stock_data(stock_path, stock_symbol, sector)
            
            if precomputed_data and detailed_data:
                try:
                    session = Session()
                    
                    # 1. Main screener table (Stocks) mein data load karte hain
                    stock_record = Stocks(**precomputed_data)
                    session.add(stock_record)
                    
                    # 2. Detailed tables mein data load karte hain
                    # Yahan hum `detailed_data` ka use karke baki tables ko load karenge
                    # Ye ek placeholder hai. Example:
                    # for row in detailed_data['profit_loss']:
                    #     session.add(ProfitLoss(stock_id=stock_record.id, **row))
                    
                    session.commit()
                    logging.info(f"Successfully loaded {stock_symbol} data into database.")
                    
                    # 3. Parquet file mein data save karte hain
                    # Hum sirf pre-computed data ko save karte hain, jo fast screening ke liye zaroori hai
                    parquet_df = pd.DataFrame([precomputed_data])
                    parquet_file_path = os.path.join(PROCESSED_DATA_DIR, f"{stock_symbol}.parquet")
                    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
                    parquet_df.to_parquet(parquet_file_path, engine='pyarrow')
                    logging.info(f"Successfully saved {stock_symbol} data to Parquet file.")
                    
                    session.close()
                    
                except SQLAlchemyError as e:
                    logging.error(f"Error loading {stock_symbol} data into database: {e}")
                    session.rollback()

    logging.info("Data pipeline execution finished.")
    
if __name__ == "__main__":
    main()


# ---------------------------------------------------------------

# data_pipeline.py (updated main function logic)

# ... (imports and other functions remain the same) ...

def main():
    """
    Main data pipeline function jo nested directories mein stocks ko process karta hai.
    """
    db_manager = Database()
    db_manager.create_tables()

    Session = sessionmaker(bind=db_manager.engine)
    
    # os.walk() ka use karke nested directories ko traverse karte hain
    for dirpath, dirnames, filenames in os.walk(RAW_DATA_ROOT_DIR):
        if 'balance_sheet.csv' in filenames:
            # Hum ek stock directory mein hain
            stock_path = dirpath
            stock_symbol = os.path.basename(stock_path)
            
            # Directory path ko split karke sector, industry, sub-industry nikalte hain
            # Example: 'Commodities/Chemicals/Fertilizer and Agrichemical/ABC Ltd'
            path_parts = dirpath.split(os.path.sep)
            
            # Aapke path structure ke hisaab se indices adjust karne padenge
            # raw_data_root_dir ke baad ke parts ko lenge
            # 'Commodities' ko chhodkar
            try:
                sector = path_parts[-3] if len(path_parts) > 3 else None
                industry = path_parts[-2] if len(path_parts) > 2 else None
                sub_industry = path_parts[-1] if len(path_parts) > 1 else None
            except IndexError:
                logging.warning(f"Could not parse full category for {stock_symbol} at {dirpath}. Skipping.")
                continue

            # Agar industry ya sub_industry missing ho toh default value set kar sakte hain
            sector = sector if sector else 'Unknown'
            industry = industry if industry else 'Unknown'
            sub_industry = sub_industry if sub_industry else 'Unknown'

            precomputed_data, detailed_data = process_stock_data(stock_path, stock_symbol, sector, industry, sub_industry)
            
            if precomputed_data and detailed_data:
                try:
                    session = Session()
                    
                    # 1. Main screener table (Stocks) mein data load karte hain
                    precomputed_data['sector'] = sector
                    precomputed_data['industry'] = industry
                    precomputed_data['sub_industry'] = sub_industry

                    stock_record = Stocks(**precomputed_data)
                    session.add(stock_record)
                    
                    # 2. Detailed tables mein data load karte hain (placeholder)
                    
                    session.commit()
                    logging.info(f"Successfully loaded {stock_symbol} data into database.")
                    
                    # 3. Parquet file mein data save karte hain
                    # ... (rest of the parquet saving logic) ...
                    
                    session.close()
                    
                except SQLAlchemyError as e:
                    logging.error(f"Error loading {stock_symbol} data into database: {e}")
                    session.rollback()

    logging.info("Data pipeline execution finished.")

# ... (The rest of the code remains the same) ...    