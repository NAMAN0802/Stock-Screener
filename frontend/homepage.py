import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Stock Screener Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


if 'saved_screeners' not in st.session_state:
    st.session_state.saved_screeners = []
if 'current_stock' not in st.session_state:
    st.session_state.current_stock = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = pd.DataFrame()
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None

css_path = os.path.join(os.path.dirname(__file__), "styles", "style.css")
with open(css_path, "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

dashboard=st.Page(
    page="pages/dashboard.py",
    title="Dashboard",
    icon="📈")

search=st.Page(
    page="pages/stock_search.py",
    title="Search Stocks",
    icon="🔍",
    default=True)

screener=st.Page(
    page="pages/screener_builder.py",
    title="Create Screener",
    icon="⚙️")

saved_screeners=st.Page(
    page="pages/saved_screeners.py",
    title="Saved Screeners",
    icon="💾")

watchlist=st.Page(
    page="pages/watchlist.py",
    title="Watchlist",
    icon="📈")

login=st.Page(
    page="pages/auth.py",
    title="Authenticate",
    icon="🔑")

page=st.navigation([dashboard,search,login,screener,saved_screeners,watchlist])
page.run()

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; margin-top: 2rem;'>
    <p>📈 Stock Screener Pro | Built with Streamlit | Data updated in real-time</p>
</div>
""", unsafe_allow_html=True)
