# pages/3_📉_Technical_Analysis.py
import streamlit as st
import pandas as pd
import numpy as np # Make sure numpy is imported
from utils.data_fetcher import get_stock_data
from components.technical_charts import plot_technical_analysis
from utils.statistics_utils import calculate_returns, calculate_statistics, plot_return_distribution, calculate_sharpe_ratio
from utils.gemini_analyzer import get_gemini_analysis

def show():
    st.title("📉 Technical Analysis & Statistics")

    if not st.session_state.get('tickers'):
        st.warning("Please select at least one stock ticker in the sidebar.")
        return

    selected_ticker = st.selectbox("Select a stock for detailed analysis:", st.session_state.tickers)

    if selected_ticker:
        start_date = st.session_state.start_date
        end_date = st.session_state.end_date

        # Fetch Data - get_stock_data returns a DataFrame with tickers as columns
        adj_close_df = get_stock_data([selected_ticker], start_date, end_date) # Pass ticker as list

        # Check if data fetching was successful and the specific ticker column exists
        if adj_close_df.empty or selected_ticker not in adj_close_df.columns:
            # Error message is likely already shown by get_stock_data
            st.error(f"Could not retrieve valid 'Adj Close' data for {selected_ticker}.")
            return # Stop execution for this ticker

        # --- Extract the Series for the selected ticker ---
        df_ticker_price = adj_close_df[selected_ticker] # Select the column -> pd.Series

        # --- Handle Volume ---
        # For accurate technical charts (Candlestick), you NEED OHLCV data.
        # If you only fetch Adj Close, volume needs simulation or separate fetching.
        # Let's stick to the simulation placeholder for now, ensuring index alignment.
        df_ticker_volume = pd.Series(dtype=float) # Initialize empty
        try:
            # --- Placeholder Volume Simulation ---
            # IMPORTANT: Replace this if you modify get_stock_data to fetch actual Volume
            st.caption("Note: Volume data is simulated for this chart.")
            np.random.seed(42) # for reproducibility
            sim_vol = 1_000_000 + 500_000 * np.random.randn(len(df_ticker_price))
            sim_vol[sim_vol < 0] = 0 # Volume cannot be negative
            df_ticker_volume = pd.Series(sim_vol, index=df_ticker_price.index, name='Volume')
            # --- End Placeholder ---

            # If you fetch real volume:
            # Example: Assume you have a function get_ohlcv(ticker, start, end)
            # ohlcv_data = get_ohlcv(selected_ticker, start_date, end_date)
            # if not ohlcv_data.empty and 'Volume' in ohlcv_data.columns:
            #     df_ticker_volume = ohlcv_data['Volume']
            # else:
            #     st.warning(f"Actual volume data not available for {selected_ticker}, simulating.")
            #     # Fallback to simulation if needed

        except Exception as vol_err:
             st.warning(f"Could not obtain or simulate volume data: {vol_err}")
             # df_ticker_volume remains empty Series, charts should handle this


        # --- Technical Chart ---
        st.header(f"Technical Chart: {selected_ticker}")
        if df_ticker_price.isnull().all():
             st.warning(f"Price data for {selected_ticker} contains only NaN values. Cannot plot chart.")
        else:
             fig_tech, technical_context = plot_technical_analysis(selected_ticker, df_ticker_price.dropna(), df_ticker_volume.reindex(df_ticker_price.dropna().index)) # Pass Series, drop NaNs for plotting robustness, align volume index
             st.plotly_chart(fig_tech, use_container_width=True)

        # --- Statistics & Distribution ---
        st.header(f"Return Statistics & Distribution: {selected_ticker}")
        returns = calculate_returns(df_ticker_price) # Use original series with NaNs kept for returns calc

        if not returns.empty and not returns.isnull().all():
            # Drop NaNs from returns before calculating stats
            returns_cleaned = returns.dropna()
            if not returns_cleaned.empty:
                stats = calculate_statistics(returns_cleaned)
                sharpe = calculate_sharpe_ratio(returns_cleaned, st.session_state.risk_free_rate)
                stats['Sharpe Ratio (Ann)'] = sharpe

                st.subheader("Key Statistics")
                # ... (rest of the statistics display code) ...
                cols = st.columns(4)
                cols[0].metric("Annualized Return", f"{stats.get('Mean Return (Ann)', 0):.2%}")
                cols[1].metric("Annualized Volatility", f"{stats.get('Volatility (Ann)', 0):.2%}")
                cols[2].metric("Sharpe Ratio", f"{stats.get('Sharpe Ratio (Ann)', 0):.2f}")
                cols[3].metric("Skewness", f"{stats.get('Skewness', 0):.2f}")

                st.subheader("Return Distribution (Bell Curve)")
                fig_dist = plot_return_distribution(returns_cleaned, selected_ticker)
                st.plotly_chart(fig_dist, use_container_width=True)

                stats_context = f"""
                Return Statistics for {selected_ticker} (based on {len(returns_cleaned)} data points):
                Annualized Mean Return: {stats.get('Mean Return (Ann)', 0):.2%}
                Annualized Volatility: {stats.get('Volatility (Ann)', 0):.2%}
                Sharpe Ratio: {stats.get('Sharpe Ratio (Ann)', 0):.2f}
                Skewness: {stats.get('Skewness', 0):.2f}
                Kurtosis: {stats.get('Kurtosis', 0):.2f}
                """
            else:
                 st.warning("Not enough valid data points after dropping NaNs to calculate statistics.")
                 stats_context = "Not enough valid data for statistical analysis."

        else:
            st.warning("Not enough data points or only NaN values to calculate returns and statistics.")
            stats_context = "Not enough data for statistical analysis."


        # --- Gemini AI Analysis Panel ---
        st.sidebar.markdown("---")
        st.sidebar.subheader("🤖 Gemini AI Analysis")
        if st.session_state.get('gemini_api_key') and st.session_state.get('gemini_model'):
             prompt_options = [
                 f"Interpret the technical indicators for {selected_ticker}. What is the current trend? Are there any buy/sell signals?",
                 f"Analyze the return distribution and statistics for {selected_ticker}. What does the skewness and kurtosis suggest about risk?",
                 f"Combine the technical signals and statistical profile for {selected_ticker}. What's the overall technical outlook?",
             ]
             chosen_prompt = st.sidebar.selectbox("Select an analysis prompt:", prompt_options, key="ta_gemini_prompt")

             if st.sidebar.button("Ask Gemini", key="ta_gemini_button"):
                 # Combine context from technical chart and stats
                 full_context = f"{technical_context}\n\n{stats_context}"
                 analysis = get_gemini_analysis(chosen_prompt, full_context)
                 with st.expander("💡 Gemini AI Insights", expanded=True):
                      st.markdown(analysis)
        else:
             st.sidebar.warning("Configure Gemini API Key in Settings to enable AI analysis.")


if __name__ == "__main__":
    # Minimal setup for direct running
    if 'tickers' not in st.session_state: st.session_state.tickers = ['AAPL', 'MSFT'] # Example
    if 'start_date' not in st.session_state: st.session_state.start_date = pd.to_datetime('2022-01-01')
    if 'end_date' not in st.session_state: st.session_state.end_date = pd.to_datetime('today')
    if 'risk_free_rate' not in st.session_state: st.session_state.risk_free_rate = 0.02
    if 'gemini_api_key' not in st.session_state: st.session_state.gemini_api_key = None
    if 'gemini_model' not in st.session_state: st.session_state.gemini_model = None
    show()