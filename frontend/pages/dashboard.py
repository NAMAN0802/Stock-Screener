import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import time

st.markdown('<h1 class="main-header">📈 Stock Screener Dashboard</h1>', unsafe_allow_html=True)
    # st.title("📈 Stock Screener Dashboard")
    
    # Market Overview
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("S&P 500", "4,150.25", "12.34 (0.30%)")
with col2:
    st.metric("NASDAQ", "12,850.75", "-25.50 (-0.20%)")
with col3:
    st.metric("DOW", "33,250.50", "45.75 (0.14%)")
with col4:
    st.metric("VIX", "18.25", "0.85 (4.88%)")

st.markdown("---")

# Quick Actions
st.subheader("🚀 Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔍 Search Stocks", use_container_width=True):
        st.session_state.page = "🔍 Stock Search"
with col2:
    if st.button("⚙️ Create Screener", use_container_width=True):
        st.session_state.page = "⚙️ Screener Builder"
with col3:
    if st.button("💾 View Saved Screeners", use_container_width=True):
        st.session_state.page = "💾 Saved Screeners"

# st.markdown("---")
# Recent Activity
st.subheader("📊 Recent Activity")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Top Gainers")
    gainers_data = pd.DataFrame({
        'Symbol': ['NVDA', 'AMD', 'TSLA'],
        'Price': [220.75, 105.25, 850.25],
        'Change %': [8.25, 6.75, 4.50]
    })
    st.dataframe(gainers_data, use_container_width=True, hide_index=True)

with col2:
    st.markdown("### Top Losers") 
    losers_data = pd.DataFrame({
        'Symbol': ['META', 'NFLX', 'GOOGL'],
        'Price': [305.50, 425.75, 2750.80],
        'Change %': [-5.25, -3.80, -2.15]
    })
    st.dataframe(losers_data, use_container_width=True, hide_index=True)

# Market Chart
st.subheader("📈 Market Trend")
dates = pd.date_range(start='2024-01-01', end='2024-12-04', freq='D')
market_data = pd.DataFrame({
    'Date': dates,
    'S&P 500': 4000 + (dates.dayofyear * 0.5) + pd.Series([i*0.1 for i in range(len(dates))])
})

fig = px.line(market_data, x='Date', y='S&P 500', title='S&P 500 YTD Performance')
st.plotly_chart(fig, use_container_width=True)
