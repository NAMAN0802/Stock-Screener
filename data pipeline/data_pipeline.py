import os
import pandas as pd
import numpy as np
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging
from database import Database
# Import all your models
from models import Stocks, ProfitLoss, BalanceSheet, CashFlow, Ratios, Shareholding, QuaterlyResults, User, SavedScreeners

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

RAW_DATA_ROOT_DIR = "D:\stock-screener\Stock-Screener\sectorwise_fundamental_data" # Your raw data root folder
PROCESSED_DATA_DIR = "processed_data"

import re 

def safe_numeric_conversion(data_obj, columns):
    """
    Safely converts specified columns to numeric, coercing errors.
    Handles both Pandas Series (e.g., summary row) and DataFrames.
    """
    if isinstance(data_obj, pd.Series):
        for col in columns:
            if col in data_obj.index:
                temp_val = data_obj[col]
                if pd.isna(temp_val) or isinstance(temp_val, (int, float, np.integer, np.floating)):
                    data_obj[col] = temp_val
                    continue

                temp_str = str(temp_val)
                numeric_match = re.search(r'[-]?\d[\d,.]*', temp_str) # Handles negative numbers and decimals

                if numeric_match:
                    cleaned_str = numeric_match.group(0).replace(',', '')
                else:
                    cleaned_str = '' 
                
                data_obj[col] = pd.to_numeric(cleaned_str, errors='coerce')

    elif isinstance(data_obj, pd.DataFrame):
        for col in columns:
            if col in data_obj.columns:
                if pd.api.types.is_object_dtype(data_obj[col]): 
                    data_obj[col] = data_obj[col].astype(str).str.extract(r'([-]?\d[\d,.]*)', expand=False)
                    data_obj[col] = data_obj[col].str.replace(',', '', regex=False)

                data_obj[col] = pd.to_numeric(data_obj[col], errors='coerce')
    return data_obj

def preprocess_financial_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms a financial DataFrame from 'wide' (metrics as rows, years as columns)
    to 'long' (years as rows, metrics as columns) and cleans it.
    """
    if df.empty:
        return pd.DataFrame()

    metric_col_name = df.columns[0]
    df_processed = df.set_index(metric_col_name).T

    df_processed.index.name = 'Period'
    df_processed = df_processed.reset_index()

    df_processed.columns = df_processed.columns.str.replace(r'\+\s*', '', regex=True).str.replace(r'%\s*', '', regex=True).str.strip()
    df_processed = df_processed.loc[:, ~df_processed.columns.duplicated()]
    df_processed['Period'] = df_processed['Period'].str.split().str[-1]
    df_processed['Period'] = pd.to_numeric(df_processed['Period'], errors='coerce').astype('Int64')
    numeric_cols = [col for col in df_processed.columns if col not in ['Period', 'TTM']] # Exclude TTM if it's a string in column names
    df_processed = safe_numeric_conversion(df_processed, numeric_cols)

    return df_processed

def preprocess_quarterly_results(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms the quarterly results DataFrame from 'wide' (metrics as rows, quarters as columns)
    to 'long' (quarters as rows, metrics as columns) and cleans it.
    """
    if df.empty:
        return pd.DataFrame()
    metric_col_name = df.columns[0]
    df_processed = df.set_index(metric_col_name).T

    df_processed.index.name = 'Period'
    df_processed = df_processed.reset_index()

    df_processed.columns = df_processed.columns.str.replace(r'\+\s*', '', regex=True).str.replace(r'%\s*', '', regex=True).str.strip()
    df_processed = df_processed.loc[:, ~df_processed.columns.duplicated()]
    numeric_cols = [col for col in df_processed.columns if col not in ['Period', 'TTM']] # Exclude TTM if it's a string in column names
    df_processed = safe_numeric_conversion(df_processed, numeric_cols)
    return df_processed

def _calculate_cagr(start_value, end_value, num_years) -> float | None:
    if num_years <= 0 or start_value is None or end_value is None or start_value <= 0:
        return None
    try:
        return ((end_value / start_value) ** (1 / num_years)) - 1
    except (ZeroDivisionError, ValueError):
        return None

def _calculate_consistency(growth_series: pd.Series) -> float | None:
    if growth_series.empty or len(growth_series) == 0:
        return None
    # Filter out NaNs before counting
    positive_growth_count = (growth_series.dropna() > 0).sum()
    total_years = growth_series.dropna().count()
    if total_years == 0:
        return None
    return positive_growth_count / total_years

def _calculate_volatility(growth_series: pd.Series) -> float | None:
    if len(growth_series.dropna()) < 2:
        return None
    try:
        return growth_series.dropna().std()
    except (TypeError, ValueError):
        return None

def calculate_ratios(data_frames: dict) -> dict:
    """
    Input dictionary of DataFrames से सारे pre-computed ratios calculate करता है.
    Returns a dictionary suitable for the Stocks model.
    """
    precomputed_fields = {}
    required_dfs = ['summary', 'profit_loss', 'balance_sheet', 'cash_flow', 'quarterly_results']

    all_present_and_not_empty = True
    for key in required_dfs:
        if key not in data_frames:
            all_present_and_not_empty = False
            break
        
        data_obj = data_frames[key]
        if isinstance(data_obj, pd.DataFrame) and data_obj.empty:
            all_present_and_not_empty = False
            break
        elif isinstance(data_obj, dict) and not data_obj: # Check if dictionary is empty
            all_present_and_not_empty = False
            break

    if not all_present_and_not_empty:
        logging.warning("One or more required dataframes are missing or empty for ratio calculation. Skipping some calculations.")
        return precomputed_fields # Return empty if core data is missing

    summary_df_series = data_frames['summary'] # This is already a Series/dict from previous step
    profit_loss_df = data_frames['profit_loss']
    balance_sheet_df = data_frames['balance_sheet']
    cash_flow_df = data_frames['cash_flow']
    quarterly_results_df = data_frames['quarterly_results']

    # --- Direct fields from summary.csv ---
    precomputed_fields['name'] = summary_df_series.get('Company Name')
    precomputed_fields['symbol'] = summary_df_series.get('NSE Link').split('=')[-1] if isinstance(summary_df_series.get('NSE Link'), str) else None
    precomputed_fields['market_cap'] = summary_df_series.get('Market Cap')
    precomputed_fields['book_value'] = summary_df_series.get('Book Value')
    precomputed_fields['roce'] = summary_df_series.get('ROCE')
    precomputed_fields['roe'] = summary_df_series.get('ROE')
    precomputed_fields['dividend_yield'] = summary_df_series.get('Dividend Yield')
    precomputed_fields['pe_ratio'] = summary_df_series.get('Stock P/E')
    precomputed_fields['current_price'] = summary_df_series.get('Current Price')

    # --- P/S Ratio (Price to Sales) ---
    if not profit_loss_df.empty and 'Sales' in profit_loss_df.columns and precomputed_fields['market_cap'] is not None:
        latest_sales = profit_loss_df.iloc[-1].get('Sales')
        eps = profit_loss_df.iloc[-1].get('EPS in Rs')
        if pd.notna(eps) and eps != 0:
            precomputed_fields['eps'] = eps
        if pd.notna(latest_sales) and latest_sales != 0:
            precomputed_fields['ps_ratio'] = precomputed_fields['market_cap'] / latest_sales
        else: precomputed_fields['ps_ratio'] = None
    else: precomputed_fields['ps_ratio'] = None

    # --- TTM P/E Ratio ---
    if not quarterly_results_df.empty and 'EPS in Rs' in quarterly_results_df.columns and summary_df_series.get('Current Price') is not None:
        ttm_eps_data = quarterly_results_df['EPS in Rs'].tail(4).sum()
        current_price = summary_df_series.get('Current Price')
        if pd.notna(ttm_eps_data) and pd.notna(current_price) and ttm_eps_data != 0:
            precomputed_fields['ttm_pe_ratio'] = current_price / ttm_eps_data
        else: precomputed_fields['ttm_pe_ratio'] = None
    else: precomputed_fields['ttm_pe_ratio'] = None

    # --- Debt to Equity Ratio ---
    if not balance_sheet_df.empty and 'Borrowings' in balance_sheet_df.columns and 'Reserves' in balance_sheet_df.columns and 'Equity Capital' in balance_sheet_df.columns:
        total_debt = balance_sheet_df.iloc[-1].get('Borrowings')
        total_equity = balance_sheet_df.iloc[-1].get('Reserves') + balance_sheet_df.iloc[-1].get('Equity Capital')
        if pd.notna(total_debt) and pd.notna(total_equity) and total_equity != 0:
            precomputed_fields['debt_to_equity'] = total_debt / total_equity
        else: precomputed_fields['debt_to_equity'] = None
    else: precomputed_fields['debt_to_equity'] = None

    # --- Current Ratio ---
    if not balance_sheet_df.empty and 'Total Assets' in balance_sheet_df.columns and 'Total Liabilities' in balance_sheet_df.columns:
        current_assets = balance_sheet_df.iloc[-1].get('Total Assets') 
        current_liabilities = balance_sheet_df.iloc[-1].get('Total Liabilities') 
        if pd.notna(current_assets) and pd.notna(current_liabilities) and current_liabilities != 0:
            precomputed_fields['current_ratio'] = current_assets / current_liabilities
        else: precomputed_fields['current_ratio'] = None
    else: precomputed_fields['current_ratio'] = None

    # --- OPM (Operating Profit Margin) ---
    if not profit_loss_df.empty and 'Operating Profit' in profit_loss_df.columns and 'Sales' in profit_loss_df.columns:
        operating_profit = profit_loss_df.iloc[-1].get('Operating Profit')
        sales = profit_loss_df.iloc[-1].get('Sales')
        if pd.notna(operating_profit) and pd.notna(sales) and sales != 0:
            precomputed_fields['opm'] = (operating_profit / sales) * 100
        else: precomputed_fields['opm'] = None
    else: precomputed_fields['opm'] = None

    # --- NPM (Net Profit Margin) ---
    if not profit_loss_df.empty and 'Net Profit' in profit_loss_df.columns and 'Sales' in profit_loss_df.columns:
        net_profit = profit_loss_df.iloc[-1].get('Net Profit')
        sales = profit_loss_df.iloc[-1].get('Sales')
        if pd.notna(net_profit) and pd.notna(sales) and sales != 0:
            precomputed_fields['npm'] = (net_profit / sales) * 100
        else: precomputed_fields['npm'] = None
    else: precomputed_fields['npm'] = None

    # --- Growth Metrics (YoY, CAGR, Volatility, Consistency, Rolling Avg) ---
    metrics_to_calculate = ['Sales', 'Net Profit', 'Cash from Operating Activity']
    dfs = {
        'Sales': profit_loss_df,
        'Net Profit': profit_loss_df,
        'Cash from Operating Activity': cash_flow_df
    }
    column_mapping = {
        'Sales': 'sales',
        'Net Profit': 'profit',
        'Cash from Operating Activity': 'operating_cash_flow'
    }

    for metric in metrics_to_calculate:
        df = dfs[metric]
        if not df.empty and metric in df.columns and len(df) >= 2:
            
            # Use `pct_change` for efficient growth calculation
            growth_series = df[metric].pct_change() * 100
            
            # --- YoY Growth ---
            yoy_growth = growth_series.iloc[-1]
            if pd.notna(yoy_growth):
                precomputed_fields[f'{column_mapping[metric]}_growth_yoy'] = yoy_growth
            
            # --- CAGR ---
            start_value = df[metric].iloc[0]
            end_value = df[metric].iloc[-1]
            num_years = len(df) - 1
            cagr = _calculate_cagr(start_value, end_value, num_years)
            if cagr is not None:
                precomputed_fields[f'{column_mapping[metric]}_cagr'] = cagr * 100
            
            # --- Consistency ---
            consistency = _calculate_consistency(growth_series)
            if consistency is not None:
                precomputed_fields[f'{column_mapping[metric]}_consistency'] = consistency
            
            # --- Volatility ---
            volatility = _calculate_volatility(growth_series)
            if volatility is not None:
                precomputed_fields[f'{column_mapping[metric]}_volatility'] = volatility
            
            # --- Rolling Average Growth (3 years) ---
            rolling_avg_growth = df[metric].rolling(window=3).mean().pct_change() * 100
            if not rolling_avg_growth.empty and pd.notna(rolling_avg_growth.iloc[-1]):
                precomputed_fields[f'{column_mapping[metric]}_rolling_avg_growth'] = rolling_avg_growth.iloc[-1]

    return precomputed_fields

def process_stock_data(stock_path: str, stock_symbol: str, sector: str, industry: str, sub_industry: str) -> tuple:
    """
    Reads CSV files for a single stock, preprocesses them, calculates ratios,
    and returns data suitable for database insertion.
    Returns: (precomputed_data_for_Stocks_table, detailed_data_for_other_tables)
    """
    if not os.path.exists(stock_path):
        logging.warning(f"Skipping {stock_symbol}: Stock data folder not found at {stock_path}.")
        return None, None

    logging.info(f"Processing data for stock: {stock_symbol} in sector: {sector}, industry: {industry}, sub_industry: {sub_industry}")
    
    raw_dfs = {}
    csv_files = ["summary.csv", "profit_loss.csv", "balance_sheet.csv", "cash_flow.csv", 
                 "quarterly_results.csv", "ratios.csv", "shareholding.csv"]
    
    for filename in csv_files:
        filepath = os.path.join(stock_path, filename)
        try:
            raw_dfs[filename.replace('.csv', '')] = pd.read_csv(filepath)
        except FileNotFoundError:
            logging.warning(f"CSV file not found for {stock_symbol}: {filename}. Providing an empty DataFrame.")
            raw_dfs[filename.replace('.csv', '')] = pd.DataFrame()
        except pd.errors.EmptyDataError:
            logging.warning(f"Empty CSV file found for {stock_symbol}: {filename}. Providing an empty DataFrame.")
            raw_dfs[filename.replace('.csv', '')] = pd.DataFrame()
        except Exception as e:
            logging.error(f"Error reading {filename} for {stock_symbol}: {e}. Providing an empty DataFrame.")
            raw_dfs[filename.replace('.csv', '')] = pd.DataFrame()

    if raw_dfs['summary'].empty:
        logging.error(f"Summary.csv is empty or missing for {stock_symbol}. Skipping full processing.")
        return None, None

    # --- Preprocess DataFrames for calculations and detailed storage ---
    preprocessed_data_for_calc_and_detail = {}
    
    if 'summary' in raw_dfs and not raw_dfs['summary'].empty:
        summary_df_raw = raw_dfs['summary']
        numeric_summary_metrics = [
            'Market Cap', 'Current Price', 'High / Low', 'Stock P/E', 
            'Book Value', 'Dividend Yield', 'ROCE', 'ROE', 'Face Value'
        ]

        if 'Metric' in summary_df_raw.columns and 'Value' in summary_df_raw.columns:
            summary_series = summary_df_raw.set_index('Metric')['Value']
            metrics_to_convert = [m for m in numeric_summary_metrics if m in summary_series.index]
            numeric_part_series = safe_numeric_conversion(summary_series.loc[metrics_to_convert].copy(), metrics_to_convert)
            final_summary_dict = {}
            for metric, value in summary_series.items():
                if metric in numeric_part_series.index:
                    final_summary_dict[metric] = numeric_part_series.get(metric)
                else:
                    final_summary_dict[metric] = value # Keep non-numeric as is
            
            preprocessed_data_for_calc_and_detail['summary'] = final_summary_dict

        else:
            # Fallback if summary.csv is not in expected 'Metric', 'Value' format
            logging.warning(f"Summary.csv for {stock_symbol} not in 'Metric', 'Value' format. Attempting direct conversion.")
            # Assume it's a single-row DataFrame with direct metric columns
            summary_series = raw_dfs['summary'].iloc[0]
            
            metrics_to_convert = [m for m in numeric_summary_metrics if m in summary_series.index]
            numeric_part_series = safe_numeric_conversion(summary_series[metrics_to_convert].copy(), metrics_to_convert)

            final_summary_dict = {}
            for metric, value in summary_series.items():
                if metric in numeric_part_series.index:
                    final_summary_dict[metric] = numeric_part_series.get(metric)
                else:
                    final_summary_dict[metric] = value
            preprocessed_data_for_calc_and_detail['summary'] = final_summary_dict
    else:
        preprocessed_data_for_calc_and_detail['summary'] = {} # Empty dict if summary missing

    # Process other financial statements (profit_loss, balance_sheet, etc.)
    dfs_to_preprocess = ['profit_loss', 'balance_sheet', 'cash_flow', 'quarterly_results', 'ratios','shareholding']
    for df_name in dfs_to_preprocess:
        if df_name in raw_dfs and not raw_dfs[df_name].empty:
            if df_name == 'quarterly_results':
                df_temp = preprocess_quarterly_results(raw_dfs[df_name])
            else:
                df_temp = preprocess_financial_df(raw_dfs[df_name])
          
            if df_name == 'profit_loss' and 'Dividend Payout' in df_temp.columns: # After cleaning 'Dividend Payout %' becomes 'Dividend Payout'
                dividend_payout_col_index = df_temp.columns.get_loc('Dividend Payout')
                # Keep 'Period' column and all columns up to and including 'Dividend Payout'
                df_temp = df_temp.iloc[:, :dividend_payout_col_index + 1] 
                logging.info(f"Removed columns after 'Dividend Payout' for {stock_symbol} profit_loss.")

            if df_name == 'quarterly_results' and 'Raw PDF' in df_temp.columns:
                df_temp = df_temp.drop(columns=['Raw PDF'])
                logging.info(f"Removed 'Raw PDF' column for {stock_symbol} quarterly_results.")

            preprocessed_data_for_calc_and_detail[df_name] = df_temp
        else:
            preprocessed_data_for_calc_and_detail[df_name] = pd.DataFrame() # Ensure empty DataFrame if missing

    preprocessed_data_for_calc_and_detail['ratios'] = raw_dfs['ratios']
    preprocessed_data_for_calc_and_detail['shareholding'] = raw_dfs['shareholding']

    detailed_data_for_db = {
        "profit_loss": preprocessed_data_for_calc_and_detail['profit_loss'].to_dict('records'),
        "balance_sheet": preprocessed_data_for_calc_and_detail['balance_sheet'].to_dict('records'),
        "cash_flow": preprocessed_data_for_calc_and_detail['cash_flow'].to_dict('records'),
        "quarterly_results": preprocessed_data_for_calc_and_detail['quarterly_results'].to_dict('records'),
        "ratios": preprocessed_data_for_calc_and_detail['ratios'].to_dict('records'), # Assuming this is already long format
        "shareholding": preprocessed_data_for_calc_and_detail['shareholding'].to_dict('records'), # Assuming this is already long format
    }
    
    precomputed_fields = calculate_ratios(preprocessed_data_for_calc_and_detail)
    
    # Create a temporary dictionary to hold the ordered fields
    ordered_fields = {}

    # Add the 'name' field first
    ordered_fields['name'] = precomputed_fields.get('name')

    # Add the new fields in the specified order
    ordered_fields['sector'] = sector
    ordered_fields['industry'] = industry
    ordered_fields['sub_industry'] = sub_industry

    # Now, add the rest of the fields from the original dictionary
    for key, value in precomputed_fields.items():
        if key not in ['name']:  # We've already handled the 'name' key
            ordered_fields[key] = value

    # Finally, replace the original dictionary with the new, ordered one
    precomputed_fields = ordered_fields
    
    return precomputed_fields, detailed_data_for_db

# Helper function to convert NumPy types to Python native types
def convert_numpy_types_recursively(data):
    """
    Recursively converts numpy data types within a dictionary to native Python types.
    """
    if isinstance(data, dict):
        return {key: convert_numpy_types_recursively(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types_recursively(item) for item in data]
    elif isinstance(data, np.int64):
        return int(data)
    elif isinstance(data, np.float64):
        return float(data)
    else:
        return data

def main():
    """
    Main data pipeline function jo nested directories mein stocks ko process karta hai.
    """
    db_manager = Database()
    if not db_manager.engine:
        logging.error("Database connection failed. Exiting pipeline.")
        return
    
    db_manager.create_tables(drop_first=False) # Create tables if they don't exist
    
    if not os.path.exists(PROCESSED_DATA_DIR):
        os.makedirs(PROCESSED_DATA_DIR)

    all_precomputed_data_for_parquet = [] # List to collect data for the final Parquet file
    
    for dirpath, dirnames, filenames in os.walk(RAW_DATA_ROOT_DIR):
        if 'summary.csv' in filenames: # Indicates a stock-specific directory
            stock_path = dirpath
            stock_symbol = os.path.basename(stock_path)
            
            # Extract sector, industry, sub_industry from path
            path_parts = dirpath.split(os.path.sep)

            sector = 'Unknown'
            industry = 'Unknown'
            sub_industry = 'Unknown'

            if len(path_parts) >= 4: # e.g., Commodities/Sector/Industry/SubIndustry/Stock
                sub_industry = path_parts[-2] # One level up from stock folder
            if len(path_parts) >= 3:
                industry = path_parts[-3] # Two levels up
            if len(path_parts) >= 2:
                sector = path_parts[-4] # Three levels up (after root_dir)

            precomputed_data, detailed_data = process_stock_data(stock_path, stock_symbol, sector, industry, sub_industry)
            
            if precomputed_data and detailed_data:
                session = db_manager.Session()
                try:
                    if not precomputed_data.get('name') or not precomputed_data.get('symbol'):
                        logging.warning(f"Skipping stock with missing name or symbol: {stock_symbol}")
                        continue # Skip this iteration and move to the next stock
                    # Delete existing records for this stock to prevent duplicates on re-run
                    existing_stock = session.query(Stocks).filter_by(symbol=stock_symbol).first()
                    if existing_stock:
                        # Delete related records first due to foreign key constraints
                        session.query(ProfitLoss).filter_by(stock_id=existing_stock.id).delete()
                        session.query(BalanceSheet).filter_by(stock_id=existing_stock.id).delete()
                        session.query(CashFlow).filter_by(stock_id=existing_stock.id).delete()
                        session.query(Ratios).filter_by(stock_id=existing_stock.id).delete()
                        session.query(Shareholding).filter_by(stock_id=existing_stock.id).delete()
                        session.query(QuaterlyResults).filter_by(stock_id=existing_stock.id).delete() # Corrected class name
                        
                        session.delete(existing_stock)
                        session.commit()
                        logging.info(f"Deleted existing records for {stock_symbol} to refresh data.")

                    # 1. Main screener table (Stocks) mein data load karte hain
                    # Filter out None values from precomputed_data to avoid SQLAlchemy errors for non-nullable columns if not all data is available
                    if 'current_price' in precomputed_data:
                        del precomputed_data['current_price']
                    precomputed_data = convert_numpy_types_recursively(precomputed_data)
                    filtered_precomputed_data = {k: v for k, v in precomputed_data.items() if v is not None}
                    stock_record = Stocks(**filtered_precomputed_data)
                    session.add(stock_record)
                    session.flush() # Flush to get the ID for foreign key relationships (stock_record.id)

                    # 2. Detailed tables mein data load karte hain
                    # Column name mappings should be verified with your actual CSV headers

                    # ProfitLoss
                    for row_data in detailed_data['profit_loss']:
                        pl_record = ProfitLoss(stock_id=stock_record.id, 
                                               year=row_data.get('Period'), # 'Period' after transpose
                                               sales=row_data.get('Sales'),
                                               expenses=row_data.get('Expenses'),
                                               revenue=row_data.get('Revenue'),
                                               operating_profit=row_data.get('Operating Profit'),
                                               opm=row_data.get('OPM'),
                                               other_income=row_data.get('Other Income'),
                                               interest=row_data.get('Interest'),
                                               depreciation=row_data.get('Depreciation'),
                                               profit_before_tax=row_data.get('Profit before tax'), # Check CSV header
                                               tax=row_data.get('Tax'),
                                               net_profit=row_data.get('Net Profit'),
                                               ebitda=row_data.get('EBITDA'), # Check CSV header
                                               eps=row_data.get('EPS in Rs'), # Check CSV header
                                               dividend_yield=row_data.get('Dividend Yield') # Check CSV header
                                               )
                        session.add(pl_record)

                    # BalanceSheet
                    for row_data in detailed_data['balance_sheet']:
                        bs_record = BalanceSheet(stock_id=stock_record.id,
                                                 year=row_data.get('Period'), # 'Period' after transpose
                                                 equity_capital=row_data.get('Equity Capital'),
                                                 reserves=row_data.get('Reserves'),
                                                 borrowings=row_data.get('Borrowings'),
                                                 other_liabilities=row_data.get('Other Liabilities'),
                                                 total_liabilities=row_data.get('Total Liabilities'),
                                                 fixed_assets=row_data.get('Fixed Assets'),
                                                 cwip=row_data.get('CWIP'), # Check CSV header
                                                 investments=row_data.get('Investments'),
                                                 other_assets=row_data.get('Other Assets'),
                                                 total_assets=row_data.get('Total Assets')
                                                 )
                        session.add(bs_record)

                    # CashFlow
                    for row_data in detailed_data['cash_flow']:
                        cf_record = CashFlow(stock_id=stock_record.id,
                                             year=row_data.get('Period'), # 'Period' after transpose
                                             cash_from_operating_activities=row_data.get('Cash from Operating Activity'),
                                             cash_from_investing_activities=row_data.get('Cash from Investing Activity'),
                                             cash_from_financing_activities=row_data.get('Cash from Financing Activity'),
                                             net_cash_flow=row_data.get('Net Cash Flow')
                                             )
                        session.add(cf_record)

                    # Ratios (Assuming your ratios.csv is already long format or doesn't need transpose)
                    for row_data in detailed_data['ratios']:
                         ratio_record = Ratios(stock_id=stock_record.id,
                                               year=row_data.get('Year'), # Assuming 'Year' is the column in ratios.csv
                                               debtor_days=row_data.get('Debtor Days'),
                                               inventory_days=row_data.get('Inventory Days'),
                                               days_payable=row_data.get('Days Payable'),
                                               cash_conversion_days=row_data.get('Cash Conversion Days'),
                                               working_capital_days=row_data.get('Working Capital Days')
                                               )
                         session.add(ratio_record)
                    
                    # Shareholding (Assuming your shareholding.csv is already long format or doesn't need transpose)
                    for row_data in detailed_data['shareholding']:
                        sh_record = Shareholding(stock_id=stock_record.id,
                                                  date=row_data.get('Date'), # Assuming 'Date' column exists
                                                  promoter_holding=row_data.get('Promoter Holding'), # Check CSV Header
                                                  fii_holding=row_data.get('FII Holding'), # Check CSV Header
                                                  dii_holding=row_data.get('DII Holding'), # Check CSV Header
                                                  government_holding=row_data.get('Government Holding'), # Check CSV Header
                                                  public_holding=row_data.get('Public Holding') # Check CSV Header
                                                  )
                        session.add(sh_record)

                    # QuarterlyResults (Corrected class name)
                    for row_data in detailed_data['quarterly_results']:
                        qr_record = QuaterlyResults(stock_id=stock_record.id,
                                                     date=row_data.get('Period'), # 'Period' after transpose
                                                     sales=row_data.get('Sales'),
                                                     expenses=row_data.get('Expenses'),
                                                     revenue=row_data.get('Revenue'),
                                                     operating_profit=row_data.get('Operating Profit'),
                                                     opm=row_data.get('OPM'),
                                                     other_income=row_data.get('Other Income'),
                                                     interest=row_data.get('Interest'),
                                                     depreciation=row_data.get('Depreciation'),
                                                     profit_before_tax=row_data.get('Profit before tax'),
                                                     tax=row_data.get('Tax'),
                                                     net_profit=row_data.get('Net Profit'),
                                                     ebitda=row_data.get('EBITDA'),
                                                     eps=row_data.get('EPS in Rs')
                                                     )
                        session.add(qr_record)


                    session.commit()
                    logging.info(f"Successfully loaded detailed data for {stock_symbol}.")
                    
                    # Add precomputed data to the list for the final Parquet file
                    all_precomputed_data_for_parquet.append(precomputed_data)
                        
                except SQLAlchemyError as e:
                    logging.error(f"SQLAlchemy Error loading {stock_symbol} data: {e}")
                    session.rollback() # Rollback on error
                except Exception as e:
                    logging.error(f"General Error processing {stock_symbol}: {e}")
                    session.rollback()
                finally:
                    session.close() # Always close the session

    # Save all precomputed data to a single Parquet file for fast reads
    if all_precomputed_data_for_parquet:
        final_df = pd.DataFrame(all_precomputed_data_for_parquet)
        parquet_path = os.path.join(PROCESSED_DATA_DIR, "all_precomputed_stocks.parquet")
        final_df.to_parquet(parquet_path, engine='pyarrow', index=False)
        logging.info(f"Successfully saved all precomputed data to {parquet_path}")

    logging.info("Data pipeline execution finished.")
    
if __name__ == "__main__":
    main()