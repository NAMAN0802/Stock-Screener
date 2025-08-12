import pandas as pd
import streamlit as st
from datetime import datetime

def fetch_stock_data(symbol):
    """Mock function to fetch stock data from backend API"""
    # Replace with actual API call: requests.get(f"http://your-backend/api/stocks/{symbol}")
    return {
        'symbol': symbol,
        'name': f'{symbol} Company',
        'price': 150.25,
        'change': 2.34,
        'change_percent': 1.58,
        'market_cap': '2.5B',
        'pe_ratio': 18.5,
        'volume': '1.2M',
        'sector': 'Technology',
        'industry': 'Software'
    }

def fetch_stock_fundamentals(symbol):
    """Mock function to fetch detailed fundamentals"""
    return {
        'balance_sheet': pd.DataFrame({
            'Year': [2023, 2022, 2021, 2020],
            'Total Assets': [1000, 950, 900, 850],
            'Total Liabilities': [400, 380, 360, 340],
            'Shareholders Equity': [600, 570, 540, 510]
        }),
        'income_statement': pd.DataFrame({
            'Year': [2023, 2022, 2021, 2020],
            'Revenue': [500, 480, 450, 420],
            'Net Income': [50, 48, 45, 42],
            'EPS': [2.5, 2.4, 2.25, 2.1]
        }),
        'ratios': {
            'ROE': 8.33,
            'ROCE': 12.5,
            'Debt_to_Equity': 0.67,
            'Current_Ratio': 2.1,
            'Quick_Ratio': 1.8
        }
    }

def search_stocks(query, filters=None):
    """Mock function to search stocks"""
    # Mock data - replace with actual API call
    mock_data = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 150.25, 'change': 2.34, 'sector': 'Technology'},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 2750.80, 'change': -15.20, 'sector': 'Technology'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'price': 310.50, 'change': 5.75, 'sector': 'Technology'},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'price': 850.25, 'change': -12.50, 'sector': 'Automotive'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corp.', 'price': 220.75, 'change': 8.25, 'sector': 'Technology'},
    ]
    return pd.DataFrame(mock_data)

def run_screener(criteria):
    """Mock function to run screener"""
    # Mock filtered results based on criteria
    filtered_data = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 150.25, 'roce': 28.5, 'pe': 18.2},
        {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'price': 310.50, 'roce': 26.8, 'pe': 22.1},
    ]
    return pd.DataFrame(filtered_data)

def save_screener(name, criteria):
    """Save screener to session state"""
    screener = {
        'name': name,
        'criteria': criteria,
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'id': len(st.session_state.saved_screeners) + 1
    }
    st.session_state.saved_screeners.append(screener)
    return screener

def login_user(username, password):
    pass

def register_user(username, password):
    pass