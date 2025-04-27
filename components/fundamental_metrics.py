import streamlit as st
import pandas as pd

def display_fundamental_metrics(ticker, info):
    """Displays key fundamental metrics in a structured way."""
    if not info:
        st.warning(f"No fundamental data available for {ticker}.")
        return

    st.subheader(f"Key Metrics for {info.get('symbol', ticker)}")
    st.write(f"**{info.get('longName', 'N/A')}** ({info.get('symbol', 'N/A')})")
    st.write(f"Sector: {info.get('sector', 'N/A')}, Industry: {info.get('industry', 'N/A')}")
    st.write(f"Website: {info.get('website', 'N/A')}")

    st.markdown("---")
    st.subheader("Valuation")
    cols_val = st.columns(4)
    cols_val[0].metric("Market Cap", f"${info.get('marketCap', 0):,}")
    cols_val[1].metric("Forward P/E", f"{info.get('forwardPE', 'N/A')}")
    cols_val[2].metric("Trailing P/E", f"{info.get('trailingPE', 'N/A')}")
    cols_val[3].metric("Price/Book", f"{info.get('priceToBook', 'N/A')}")
    cols_val = st.columns(4)
    cols_val[0].metric("PEG Ratio", f"{info.get('pegRatio', 'N/A')}")
    cols_val[1].metric("Price/Sales (TTM)", f"{info.get('priceToSalesTrailing12Months', 'N/A')}")
    cols_val[2].metric("Enterprise Value", f"${info.get('enterpriseValue', 0):,}")
    cols_val[3].metric("EV/Revenue", f"{info.get('enterpriseToRevenue', 'N/A')}")


    st.markdown("---")
    st.subheader("Profitability & Efficiency")
    cols_prof = st.columns(4)
    cols_prof[0].metric("Profit Margin", f"{info.get('profitMargins', 0):.2%}")
    cols_prof[1].metric("Operating Margin (TTM)", f"{info.get('operatingMargins', 0):.2%}")
    cols_prof[2].metric("Return on Assets (TTM)", f"{info.get('returnOnAssets', 0):.2%}")
    cols_prof[3].metric("Return on Equity (TTM)", f"{info.get('returnOnEquity', 0):.2%}")

    st.markdown("---")
    st.subheader("Growth")
    cols_growth = st.columns(3)
    cols_growth[0].metric("Revenue Growth (YoY)", f"{info.get('revenueGrowth', 0):.2%}")
    cols_growth[1].metric("Earnings Growth (YoY)", f"{info.get('earningsGrowth', 'N/A')}") # May not be available directly
    cols_growth[2].metric("Quarterly Revenue Growth (YoY)", f"{info.get('revenueQuarterlyGrowth', 'N/A')}") # Check key name

    st.markdown("---")
    st.subheader("Dividends & Financial Health")
    cols_fin = st.columns(4)
    cols_fin[0].metric("Dividend Yield", f"{info.get('dividendYield', 0):.2%}")
    cols_fin[1].metric("Payout Ratio", f"{info.get('payoutRatio', 0):.2%}")
    cols_fin[2].metric("Debt/Equity", f"{info.get('debtToEquity', 'N/A')}")
    cols_fin[3].metric("Current Ratio", f"{info.get('currentRatio', 'N/A')}")

    st.markdown("---")
    st.subheader("Summary")
    st.expander("Business Summary").write(info.get('longBusinessSummary', 'No summary available.'))

    # Prepare data for Gemini
    fundamental_context = f"""
    Fundamental Data for {info.get('symbol', ticker)} ({info.get('longName', '')}):
    Sector: {info.get('sector', 'N/A')}
    Industry: {info.get('industry', 'N/A')}
    Market Cap: {info.get('marketCap', 0):,}
    Forward P/E: {info.get('forwardPE', 'N/A')}
    Trailing P/E: {info.get('trailingPE', 'N/A')}
    Price/Book: {info.get('priceToBook', 'N/A')}
    PEG Ratio: {info.get('pegRatio', 'N/A')}
    Profit Margin: {info.get('profitMargins', 0):.2%}
    ROE (TTM): {info.get('returnOnEquity', 0):.2%}
    Revenue Growth (YoY): {info.get('revenueGrowth', 0):.2%}
    Debt/Equity: {info.get('debtToEquity', 'N/A')}
    Dividend Yield: {info.get('dividendYield', 0):.2%}
    Business Summary: {info.get('longBusinessSummary', 'N/A')[:500]}...
    """
    return fundamental_context


def display_recommendations(ticker, recommendations):
    """Displays analyst recommendations."""
    st.subheader(f"Analyst Recommendations for {ticker}")
    if recommendations is None or recommendations.empty:
        st.write("No recommendation data available.")
        return

    st.dataframe(recommendations.head(), use_container_width=True)
    # Could add a chart showing trend of recommendations over time

def display_earnings_history(ticker, earnings):
    """Displays earnings history."""
    st.subheader(f"Earnings History for {ticker}")
    if earnings is None or earnings.empty:
        st.write("No earnings history available.")
        return

    st.dataframe(earnings, use_container_width=True)
    # Could add a chart comparing Actual vs Estimate EPS