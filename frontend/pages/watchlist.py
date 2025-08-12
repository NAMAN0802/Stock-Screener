import streamlit as st
import pandas as pd

st.markdown('<h1 class="main-header">📈 My Watchlist</h1>', unsafe_allow_html=True)
    # Mock watchlist data
watchlist_data = pd.DataFrame({
    'Symbol': ['AAPL', 'GOOGL', 'MSFT', 'TSLA'],
    'Name': ['Apple Inc.', 'Alphabet Inc.', 'Microsoft Corp.', 'Tesla Inc.'],
    'Price': [150.25, 2750.80, 310.50, 850.25],
    'Change': [2.34, -15.20, 5.75, -12.50],
    'Change %': [1.58, -0.55, 1.89, -1.45],
    'Alert Price': [145.00, 2800.00, 300.00, 900.00]
})

# Add/Remove stocks
col1, col2 = st.columns([3, 1])

with col1:
    new_stock = st.text_input("Add stock to watchlist", placeholder="Enter stock symbol")

with col2:
    st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
    if st.button("➕ Add", use_container_width=True):
        if new_stock:
            st.success(f"Added {new_stock} to watchlist!")

# Display watchlist
st.subheader("📊 Your Stocks")

for idx, row in watchlist_data.iterrows():
    with st.container():
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 1])
        
        with col1:
            st.write(f"**{row['Symbol']}**")
            st.write(row['Name'])
        
        with col2:
            st.write(f"**${row['Price']:.2f}**")
            change_color = "positive" if row['Change'] > 0 else "negative"
            st.markdown(f'<span class="{change_color}">{row["Change"]:+.2f} ({row["Change %"]:+.2f}%)</span>', unsafe_allow_html=True)
        
        with col3:
            st.write(f"Alert: ${row['Alert Price']:.2f}")
        
        with col4:
            if st.button("📊", key=f"wl_details_{row['Symbol']}", help="View Details"):
                st.session_state.current_stock = row['Symbol']
        
        with col5:
            if st.button("🔔", key=f"wl_alert_{row['Symbol']}", help="Set Alert"):
                st.info("Alert settings would open here")
        
        with col6:
            if st.button("❌", key=f"wl_remove_{row['Symbol']}", help="Remove"):
                st.success(f"Removed {row['Symbol']} from watchlist!")
        
        st.markdown("---")