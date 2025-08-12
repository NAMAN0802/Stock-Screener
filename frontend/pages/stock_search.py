import streamlit as st
import pandas as pd
from utils.apis import search_stocks
from pages.stock_details import display_stock_details

st.markdown('<h1 class="main-header">🔍 Stock Search</h1>', unsafe_allow_html=True)

# Search Interface
col1, col2 = st.columns([3, 1])

with col1:
    # search_query = st.text_input("Search stocks by symbol or company name", placeholder="e.g., AAPL, Apple, Microsoft")
    all_stocks = search_stocks("")  # Get all stock symbols
    suggestion_list = [f"{row['symbol']} - {row['name']}" for _, row in all_stocks.iterrows()]

    search_query = st.selectbox(
        label="Search stocks by symbol or company name",
        options=suggestion_list,
        placeholder="e.g., AAPL, Apple, Microsoft",
        index=None
    )

with col2:
    st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
    button = st.button("🔍 Search", use_container_width=True)
    if button and search_query:
        symbol = search_query.split(" - ")[0].strip()
        st.session_state.current_stock = search_query
           
if button: 
    display_stock_details()