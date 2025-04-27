# utils/data_fetcher.py

import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime
import traceback # For detailed error logging

# =============================================
# === STOCK PRICE DATA (Adjusted Close) =====
# =============================================
@st.cache_data(ttl=3600) # Cache data for 1 hour
def get_stock_data(tickers, start_date, end_date):
    """
    Fetches historical stock data (Adjusted Close) for one or more tickers.

    Args:
        tickers (list or str): A list of ticker symbols or a single ticker string.
        start_date (datetime.date): Start date for data fetching.
        end_date (datetime.date): End date for data fetching.

    Returns:
        pd.DataFrame: A DataFrame containing the 'Adj Close' prices for the requested tickers,
                      with tickers as column names. Returns an empty DataFrame on failure.
    """
    # Ensure tickers is a list
    if isinstance(tickers, str):
        tickers = [tickers.strip().upper()]
    elif isinstance(tickers, list):
        tickers = [t.strip().upper() for t in tickers if isinstance(t, str) and t.strip()]
    else:
        st.error("Invalid ticker format. Please provide a string or a list of strings.")
        return pd.DataFrame()

    if not tickers:
        # st.warning("No valid tickers provided.") # Optional warning
        return pd.DataFrame()

    num_tickers = len(tickers)
    # st.write(f"Fetching Adj Close for: {', '.join(tickers)}") # Debugging fetch

    try:
        # Download data using yfinance
        data = yf.download(
            tickers=tickers,
            start=start_date,
            end=end_date,
            progress=False, # Set to True for visual progress in console
            # group_by='ticker' # Alternative grouping, but default is usually fine
            auto_adjust=False # Set to False to get 'Adj Close' explicitly
        )

        if data.empty:
            st.error(f"No data downloaded for {', '.join(tickers)}. Check symbols/dates.")
            return pd.DataFrame()

        # --- Process the downloaded data to extract 'Adj Close' ---

        # Case 1: Multiple tickers OR Single ticker returned with MultiIndex columns
        if isinstance(data.columns, pd.MultiIndex):
            try:
                 # Select only the 'Adj Close' price for all tickers
                 adj_close_data = data.xs('Adj Close', level=0, axis=1)
                 # Reindex to ensure all requested tickers are present, even if some failed partially
                 adj_close_data = adj_close_data.reindex(columns=tickers)

            except KeyError:
                 # If 'Adj Close' is not found (e.g., different yf version or data source issue)
                 st.error(f"Could not find 'Adj Close' column level for {', '.join(tickers)}.")
                 print("Available Columns:", data.columns) # Debug print
                 return pd.DataFrame()

        # Case 2: Single ticker returned with simple columns (no MultiIndex)
        elif num_tickers == 1 and not isinstance(data.columns, pd.MultiIndex):
            ticker = tickers[0]
            if 'Adj Close' in data.columns:
                # Select the 'Adj Close' column and rename it to the ticker symbol
                adj_close_data = data[['Adj Close']].rename(columns={'Adj Close': ticker})
            else:
                st.error(f"'Adj Close' column not found for single ticker {ticker}.")
                print("Available Columns:", data.columns) # Debug print
                return pd.DataFrame()

        # Case 3: Unexpected structure
        else:
            st.error(f"Unexpected data structure received from yfinance for {', '.join(tickers)}.")
            print("Columns Type:", type(data.columns))
            print("Columns:", data.columns)
            return pd.DataFrame()

        # --- Final Checks ---
        all_nan_cols = adj_close_data.columns[adj_close_data.isnull().all()].tolist()
        if all_nan_cols:
            st.warning(f"Data for ticker(s) {', '.join(all_nan_cols)} consists entirely of NaN values.")
            # Keep them for now, downstream functions should handle NaN

        return adj_close_data

    except Exception as e:
        st.error(f"Error during data download/processing for {', '.join(tickers)}: {e}")
        st.error("Traceback:")
        st.code(traceback.format_exc()) # Show detailed traceback
        return pd.DataFrame()


# =============================================
# === FUNDAMENTAL & OTHER INFO ==============
# =============================================

@st.cache_data(ttl=3600) # Cache for 1 hour
def get_stock_info(ticker):
    """Fetches fundamental information for a single ticker."""
    try:
        stock = yf.Ticker(ticker)
        # .info can be slow or fail; consider alternatives if performance is critical
        info = stock.info
        # Basic validation: Check if the fetched info seems related to the requested ticker
        if not info or 'symbol' not in info or info.get('symbol', '').upper() != ticker.upper():
             # Handle cases where yfinance might return info for a different ticker (e.g., redirects)
             # Or if info is empty/incomplete
             st.warning(f"Could not retrieve complete or accurate info for {ticker}. Ticker might be invalid, delisted, or data unavailable.", icon="⚠️")
             return None
        return info
    except Exception as e:
        # Handle potential network errors, timeouts, or parsing issues
        st.error(f"Error fetching info for {ticker}: {e}")
        # Optionally log the error for debugging
        # print(f"Detailed error fetching info for {ticker}: {traceback.format_exc()}")
        return None


@st.cache_data(ttl=86400) # Cache longer, recommendations don't change that often
def get_recommendations(ticker):
    """Fetches analyst recommendations."""
    try:
        stock = yf.Ticker(ticker)
        recom = stock.recommendations
        # Filter for recent recommendations if needed
        if recom is not None and not recom.empty:
            # Convert index to Datetime objects if they are not already
            recom.index = pd.to_datetime(recom.index)
            # Sort by date descending to show the latest first
            recom = recom.sort_index(ascending=False)
        else:
             return pd.DataFrame() # Return empty if None or empty
        return recom
    except Exception as e:
        st.warning(f"Could not fetch recommendations for {ticker}: {e}", icon="⚠️")
        return pd.DataFrame() # Return empty dataframe on error


@st.cache_data(ttl=86400) # Cache earnings history
def get_earnings_history(ticker):
    """Fetches earnings history."""
    try:
        stock = yf.Ticker(ticker)
        earnings = stock.earnings_history
        if earnings is not None and not earnings.empty:
             # Sort by date descending (often index is already date-like)
             try:
                 earnings = earnings.sort_index(ascending=False)
             except TypeError:
                 # Handle cases where index might not be directly sortable (less common)
                 pass
        else:
            return pd.DataFrame() # Return empty if None or empty
        return earnings
    except Exception as e:
        st.warning(f"Could not fetch earnings history for {ticker}: {e}", icon="⚠️")
        return pd.DataFrame()

# =============================================
# === (Optional: Add other fetchers here) =====
# =============================================
# e.g., get_ohlcv_data if needed for candlestick charts