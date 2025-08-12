import streamlit as st
import pandas as pd
import plotly.express as px
from utils.apis import fetch_stock_data, fetch_stock_fundamentals

def display_stock_details():
    if st.session_state.current_stock:
        symbol = st.session_state.current_stock
        stock_data = fetch_stock_data(symbol)
        fundamentals = fetch_stock_fundamentals(symbol)
        
        st.markdown(f'<h1 class="main-header">📊 {symbol} - Stock Details</h1>', unsafe_allow_html=True)
        
        # Stock Overview
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Price", f"${stock_data['price']}", f"{stock_data['change']:+.2f}")
        with col2:
            st.metric("Market Cap", stock_data['market_cap'])
        with col3:
            st.metric("P/E Ratio", stock_data['pe_ratio'])
        with col4:
            st.metric("Volume", stock_data['volume'])
        with col5:
            st.metric("Sector", stock_data['sector'])
        
        # Tabs for detailed information
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Chart", "💰 Financials", "📊 Ratios", "🏢 Peer Comparison", "📋 Summary"])
        
        with tab1:
            # Mock price chart
            dates = pd.date_range(start='2024-01-01', end='2024-08-04', freq='D')
            price_data = pd.DataFrame({
                'Date': dates,
                'Price': stock_data['price'] + pd.Series([i*0.01 for i in range(len(dates))])
            })
            
            fig = px.line(price_data, x='Date', y='Price', title=f'{symbol} Price Chart')
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart
            volume_data = pd.DataFrame({
                'Date': dates,
                'Volume': [1000000 + i*1000 for i in range(len(dates))]
            })
            
            fig_volume = px.bar(volume_data, x='Date', y='Volume', title=f'{symbol} Volume')
            st.plotly_chart(fig_volume, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Balance Sheet")
                st.dataframe(fundamentals['balance_sheet'], use_container_width=True)
            
            with col2:
                st.subheader("Income Statement")
                st.dataframe(fundamentals['income_statement'], use_container_width=True)
        
        with tab3:
            st.subheader("Key Ratios")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("ROE (%)", f"{fundamentals['ratios']['ROE']:.2f}")
                st.metric("ROCE (%)", f"{fundamentals['ratios']['ROCE']:.2f}")
            
            with col2:
                st.metric("Debt/Equity", f"{fundamentals['ratios']['Debt_to_Equity']:.2f}")
                st.metric("Current Ratio", f"{fundamentals['ratios']['Current_Ratio']:.2f}")
            
            with col3:
                st.metric("Quick Ratio", f"{fundamentals['ratios']['Quick_Ratio']:.2f}")
        
        with tab4:
            st.subheader("Peer Comparison")
            
            peer_data = pd.DataFrame({
                'Company': [symbol, 'Peer 1', 'Peer 2', 'Peer 3'],
                'P/E Ratio': [18.5, 20.2, 16.8, 22.1],
                'ROE (%)': [8.33, 7.85, 9.12, 6.98],
                'Debt/Equity': [0.67, 0.72, 0.58, 0.81]
            })
            
            st.dataframe(peer_data, use_container_width=True, hide_index=True)
            
            # Peer comparison chart
            fig = px.bar(peer_data, x='Company', y='P/E Ratio', title='P/E Ratio Comparison')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab5:
            st.subheader("Company Summary")
            st.write(f"""
            **{stock_data['name']}** operates in the **{stock_data['sector']}** sector, 
            specifically in **{stock_data['industry']}**. The company has shown strong 
            fundamentals with a current P/E ratio of {stock_data['pe_ratio']} and 
            market capitalization of {stock_data['market_cap']}.
            
            **Key Highlights:**
            - Strong balance sheet with healthy cash flows
            - Consistent revenue growth over the past years
            - Competitive position in the industry
            - Experienced management team
            """)

    else:
        st.warning("Please select a stock from the search page to view details.")
        if st.button("🔍 Go to Stock Search"):
            st.session_state.page = "🔍 Stock Search"
