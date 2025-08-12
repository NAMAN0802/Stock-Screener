import streamlit as st
import pandas as pd
from utils.apis import run_screener, save_screener

st.markdown('<h1 class="main-header">⚙️ Build Custom Screener</h1>', unsafe_allow_html=True)
    
    # Screener Name
screener_name = st.text_input("Screener Name", placeholder="e.g., High ROE Banking Stocks")

st.subheader("📊 Screening Criteria")

# Two column layout
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💰 Financial Metrics")

    # ROE
    roe_enabled = st.checkbox("Return on Equity (ROE)")
    if roe_enabled:
        roe_min = st.number_input("ROE Min (%)", value=15.0)
        roe_max = st.number_input("ROE Max (%)", value=50.0)

    # ROCE
    roce_enabled = st.checkbox("Return on Capital Employed (ROCE)")
    if roce_enabled:
        roce_min = st.number_input("ROCE Min (%)", value=20.0)
        roce_max = st.number_input("ROCE Max (%)", value=50.0)

    # PE Ratio
    pe_enabled = st.checkbox("P/E Ratio")
    if pe_enabled:
        pe_min = st.number_input("P/E Min", value=5.0)
        pe_max = st.number_input("P/E Max", value=25.0)

    # Debt to Equity
    de_enabled = st.checkbox("Debt to Equity")
    if de_enabled:
        de_max = st.number_input("Max D/E Ratio", value=0.5)

with col2:
    st.markdown("### 🏢 Company Filters")

    # Market Cap
    market_cap_filter = st.selectbox(
        "Market Cap",
        ["Any", "Large Cap (>$10B)", "Mid Cap ($2B-$10B)", "Small Cap (<$2B)"]
    )

    # Sector
    sector_filter = st.multiselect(
        "Sectors",
        ["Technology", "Healthcare", "Finance", "Energy", "Consumer", "Industrial"]
    )

    # Industry
    industry_filter = st.multiselect(
        "Industries",
        ["Banking", "Software", "Pharmaceuticals", "Oil & Gas", "Retail"]
    )

    # Price Range
    price_enabled = st.checkbox("Price Range")
    if price_enabled:
        price_min = st.number_input("Min Price ($)", value=10.0)
        price_max = st.number_input("Max Price ($)", value=500.0)

# Form only contains the submit buttons now
with st.form("screener_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        test_screener = st.form_submit_button("🧪 Test Screener", use_container_width=True)
    
    with col2:
        save_screener_btn = st.form_submit_button("💾 Save Screener", use_container_width=True)
    
    with col3:
        clear_form = st.form_submit_button("🗑️ Clear All", use_container_width=True)

# Form submission handlers
if test_screener:
    # Build criteria dict
    criteria = {}
    if roe_enabled:
        criteria['roe'] = {'min': roe_min, 'max': roe_max}
    if roce_enabled:
        criteria['roce'] = {'min': roce_min, 'max': roce_max}
    if pe_enabled:
        criteria['pe'] = {'min': pe_min, 'max': pe_max}
    if de_enabled:
        criteria['debt_equity'] = {'max': de_max}
    if price_enabled:
        criteria['price'] = {'min': price_min, 'max': price_max}
    if market_cap_filter != "Any":
        criteria['market_cap'] = market_cap_filter
    if sector_filter:
        criteria['sectors'] = sector_filter
    if industry_filter:
        criteria['industries'] = industry_filter

    # Run screener (you need to define this function)
    st.subheader("🔍 Screener Results")
    results = run_screener(criteria)

    if not results.empty:
        st.success(f"Found {len(results)} stocks matching your criteria!")
        st.dataframe(results, use_container_width=True, hide_index=True)
    else:
        st.warning("No stocks found matching your criteria. Try adjusting the parameters.")

if save_screener_btn:
    if screener_name:
        if not st.session_state.get("logged_in"):
            st.warning("You must be logged in to save screeners.")
            st.switch_page("pages/auth.py")
        elif not screener_name:
            st.error("Please enter a screener name.")
        else:
        # Save criteria
            criteria = {}
            if roe_enabled:
                criteria['roe'] = {'min': roe_min, 'max': roe_max}
            if roce_enabled:
                criteria['roce'] = {'min': roce_min, 'max': roce_max}
            if pe_enabled:
                criteria['pe'] = {'min': pe_min, 'max': pe_max}
            if de_enabled:
                criteria['debt_equity'] = {'max': de_max}
            if price_enabled:
                criteria['price'] = {'min': price_min, 'max': price_max}
            if market_cap_filter != "Any":
                criteria['market_cap'] = market_cap_filter
            if sector_filter:
                criteria['sectors'] = sector_filter
            if industry_filter:
                criteria['industries'] = industry_filter

            saved = save_screener(screener_name, criteria)
            st.success(f"Screener '{screener_name}' saved successfully!")
    else:
        st.error("Please enter a screener name.")

if clear_form:
    st.experimental_rerun()  # This resets all fields