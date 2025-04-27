# Personalized Stock Analyzer & Portfolio Manager

This Streamlit application provides a comprehensive toolkit for stock analysis and portfolio management, integrating various financial techniques and AI-powered insights.

## Features

*   **Ticker Management**: Add multiple stock tickers and define custom date ranges.
*   **Real-Time Data**: Fetches stock data using `yfinance`.
*   **Fundamental Analysis**: Displays key financial metrics (P/E, P/B, ROE, etc.), analyst recommendations, and earnings history.
*   **Technical Analysis**: Visualizes price trends, Moving Averages (SMA, EMA), RSI, MACD, and Bollinger Bands. Includes volume analysis.
*   **Statistical Analysis**: Shows return distributions (bell curve), calculates key statistics (mean, volatility, Sharpe Ratio, skewness, kurtosis).
*   **Modern Portfolio Theory (MPT)**:
    *   Calculates and plots the Efficient Frontier.
    *   Identifies Minimum Risk and Maximum Sharpe Ratio portfolios.
    *   Displays optimal portfolio weights, expected return, and volatility.
*   **Bootstrapping Simulation**: Simulates potential future portfolio returns based on historical data resampling.
*   **Bulk Deal Tracking**: (Placeholder) A section to monitor significant market deals.
*   **Gemini AI Integration**: Provides AI-powered analysis and interpretation of financial data and charts on relevant pages (requires API key).
*   **Personalization**: Saves selected tickers and settings within the current session. Allows configuration of parameters like the risk-free rate.

## Project Structure

---

# 📂 Full Project Structure for Your Personalized Stock Analyzer

```
personalized_stock_analyzer/
│
├── 📄 streamlit_app.py          # Main entry point of the app
│
├── 📁 pages/                    # Optional - for multi-page setup
│   ├── 1_Dashboard.py           # Overview dashboard: quick stats, portfolio summary
│   ├── 2_Fundamental_Analysis.py # Detailed fundamental metrics
│   ├── 3_Technical_Analysis.py   # Charts like MA, RSI, Bollinger Bands
│   ├── 4_Portfolio_Optimization.py # Modern Portfolio Theory + Efficient Frontier
│   ├── 5_Bulk_Deals_Tracker.py   # Bulk/Block deals page
│   ├── 6_Settings.py             # User settings like saved tickers, preferences
│
├── 📁 components/               # For reusable Streamlit components
│   ├── stock_selector.py         # Ticker selection UI
│   ├── fundamental_metrics.py    # Display fundamental stats nicely
│   ├── technical_charts.py        # Display Bollinger Bands, RSI, etc.
│   ├── portfolio_charts.py        # Efficient frontier, bell curves
│   ├── bulk_deals_table.py        # Table or visualization for bulk deals
│
├── 📁 utils/                     # Helper functions and data fetching
│   ├── data_fetcher.py            # yfinance data downloaders
│   ├── portfolio_optimizer.py     # Mean-Variance Optimization functions
│   ├── bootstrap_simulator.py     # Bootstrapping simulations
│   ├── statistics_utils.py        # Bell curve, Sharpe ratio, skewness etc.
│   ├── bulk_deals_scraper.py      # Web scraper or API handler for bulk deals
│
├── 📁 assets/                    # Images, logos, CSS styling (if needed)
│   ├── logo.png
│   ├── custom_styles.css
│
├── 📄 requirements.txt           # Python dependencies (yfinance, pandas, numpy, etc.)
│
└── 📄 README.md                   # Instructions and description of the app
```

---

# 🛠️ Modular Breakdown

| Folder/File | Purpose |
|:------------|:--------|
| **streamlit_app.py** | High-level Streamlit app setup, main sidebar, routing to pages. |
| **pages/** | All different pages — dashboard, analysis, portfolio selection etc. |
| **components/** | Modular UI elements you can reuse across pages (tickers, charts). |
| **utils/** | All heavy lifting - data fetching, calculations, portfolio theory. |
| **assets/** | Make your app look polished (logo, simple CSS if needed). |

---

# 📜 Suggestion for Routing (inside `streamlit_app.py`)

```python
import streamlit as st

st.set_page_config(page_title="Personal Stock Analyzer", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Dashboard",
    "Fundamental Analysis",
    "Technical Analysis",
    "Portfolio Optimization",
    "Bulk Deals Tracker",
    "Settings"
])

if page == "Dashboard":
    import pages.Dashboard as db
    db.show()

elif page == "Fundamental Analysis":
    import pages.Fundamental_Analysis as fa
    fa.show()

elif page == "Technical Analysis":
    import pages.Technical_Analysis as ta
    ta.show()

elif page == "Portfolio Optimization":
    import pages.Portfolio_Optimization as po
    po.show()

elif page == "Bulk Deals Tracker":
    import pages.Bulk_Deals_Tracker as bd
    bd.show()

elif page == "Settings":
    import pages.Settings as stg
    stg.show()
```

---

# 📦 Key Python Packages You'd Use

- `streamlit`
- `yfinance`
- `numpy`
- `pandas`
- `matplotlib`
- `seaborn`
- `scipy` (for optimization and distributions)
- `scikit-learn` (for bootstrapping and simulations)
- `cvxpy` (for more advanced portfolio optimization if needed)

---

# 🌟 Summary

You’ll have:
- A **real-time data** powered stock analyzer.
- A full **Modern Portfolio Theory** optimizer.
- **Technical + fundamental** deep dives.
- **Bell curve / Bootstrapping** simulations.
- A **professional, clean, expandable** project structure.

---

"BellCurve Securities — Intelligent investing, optimized for you."


Would you also like me to draft **the user flow** (step-by-step how a typical user session would work)?  
That will make it even easier for you to build or even pass to a developer! 🚀  
Want me to? 🎯