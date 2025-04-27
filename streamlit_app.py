import streamlit as st
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="HyperPersonalized Stock Analyzer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Title ---
st.title("🚀 HyperPersonalized Stock Analyzer & Portfolio Manager")
st.caption("Powered by yfinance, MPT, Bootstrapping, TA/FA & Gemini AI")

# --- Initialize Session State ---
# Use session state to store user inputs and selections across pages
if 'tickers' not in st.session_state:
    st.session_state.tickers = [] # Default or example tickers ['AAPL', 'MSFT', 'GOOGL']
if 'start_date' not in st.session_state:
    st.session_state.start_date = datetime.now().date() - timedelta(days=365 * 2)
if 'end_date' not in st.session_state:
    st.session_state.end_date = datetime.now().date()
if 'portfolio_tickers' not in st.session_state:
    st.session_state.portfolio_tickers = []
if 'risk_free_rate' not in st.session_state:
    st.session_state.risk_free_rate = 0.02 # Default 2%
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = None
if 'gemini_model' not in st.session_state:
    st.session_state.gemini_model = None # Will be initialized in settings/gemini_analyzer

# --- Sidebar Introduction ---
st.sidebar.success("Select an analysis page above.")

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **About:** This app performs stock analysis using various techniques
    including Fundamental Analysis, Technical Analysis, Modern Portfolio Theory (MPT),
    and Bootstrapping simulations. It integrates real-time data via yfinance
    and offers AI-powered insights via Google Gemini.
    """
)
st.sidebar.markdown("---")
st.sidebar.header("Global Settings")

# --- Global Ticker Input ---
# We can put the main ticker selection here or within specific pages.
# Let's put it here for easy access across FA/TA pages.
st.sidebar.subheader("Select Stocks for Analysis")
tickers_input = st.sidebar.text_input("Enter Stock Tickers (comma-separated)",
                                      value=", ".join(st.session_state.tickers),
                                      key="sidebar_ticker_input")
if tickers_input:
    st.session_state.tickers = [ticker.strip().upper() for ticker in tickers_input.split(',') if ticker.strip()]

# --- Global Date Range Input ---
st.sidebar.subheader("Select Date Range")
col1, col2 = st.sidebar.columns(2)
with col1:
    st.session_state.start_date = st.date_input("Start Date", st.session_state.start_date)
with col2:
    st.session_state.end_date = st.date_input("End Date", st.session_state.end_date)

# Validate dates
if st.session_state.start_date >= st.session_state.end_date:
    st.sidebar.error("Error: End date must fall after start date.")

st.sidebar.markdown("---")
st.sidebar.caption(f"Current Tickers: {', '.join(st.session_state.tickers) if st.session_state.tickers else 'None'}")
st.sidebar.caption(f"Date Range: {st.session_state.start_date} to {st.session_state.end_date}")
st.sidebar.caption(f"Risk-Free Rate: {st.session_state.risk_free_rate:.2%}")

# --- Main Area Welcome Message ---
st.markdown(
    """
    Welcome to your personalized stock analysis dashboard!

    **Navigate using the sidebar on the left to explore different analysis modules:**

    *   **📈 Dashboard:** Get a quick overview (placeholder).
    *   **📊 Fundamental Analysis:** Examine key financial metrics and company info.
    *   **📉 Technical Analysis:** Visualize price trends, indicators (like Bollinger Bands), and volume.
    *   **💼 Portfolio Optimization:** Build and optimize portfolios using Modern Portfolio Theory.
    *   **📰 Bulk Deals Tracker:** Monitor significant market transactions (placeholder).
    *   **⚙️ Settings:** Configure API keys, risk-free rate, and other preferences.

    Select tickers and a date range in the sidebar to begin your analysis.
    """
)

st.info("Note: Data is sourced from Yahoo Finance and may have delays or inaccuracies. AI insights are for informational purposes only.")

# (Streamlit automatically handles navigation based on files in the 'pages' directory)