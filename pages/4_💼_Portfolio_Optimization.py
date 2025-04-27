import streamlit as st
import pandas as pd
import numpy as np
from components.stock_selector import render_portfolio_selector
from utils.data_fetcher import get_stock_data
from utils.statistics_utils import calculate_returns
from utils.portfolio_optimizer import (calculate_portfolio_performance,
                                       generate_efficient_frontier,
                                       find_optimal_portfolio)
from utils.bootstrap_simulator import run_bootstrap_simulation, plot_simulation_histogram
from components.portfolio_charts import plot_efficient_frontier, display_portfolio_summary
from utils.gemini_analyzer import get_gemini_analysis

def show():
    st.title("💼 Portfolio Optimization (Modern Portfolio Theory)")

    # --- Portfolio Stock Selection ---
    portfolio_tickers = render_portfolio_selector()

    if len(portfolio_tickers) < 2:
        st.info("Please select at least two stocks for portfolio optimization.")
        return

    start_date = st.session_state.start_date
    end_date = st.session_state.end_date
    risk_free_rate = st.session_state.risk_free_rate

    # --- Fetch Data ---
    data = get_stock_data(portfolio_tickers, start_date, end_date)

    if data.empty or data.isnull().values.any():
        st.error("Could not fetch valid data for all selected portfolio tickers. Check symbols or date range.")
        # Optionally display which tickers failed if data_fetcher provides more info
        return

    # --- Calculate Returns & Covariance ---
    returns = calculate_returns(data)
    if returns.empty or returns.shape[0] < 2: # Need at least 2 data points for covariance
         st.error("Not enough historical data in the selected range to perform optimization.")
         return

    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    # --- Optimization Setup ---
    num_assets = len(portfolio_tickers)
    # Constraints: sum of weights = 1
    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
    # Bounds: weights between 0 and 1 (no short selling)
    bounds = tuple((0.0, 1.0) for _ in range(num_assets))

    # --- Run Optimization & Generate Frontier ---
    st.header("Efficient Frontier")
    num_portfolios_slider = st.slider("Number of portfolios to simulate for Frontier:", 50, 500, 100, key="num_portfolios")

    try:
        results_df = generate_efficient_frontier(mean_returns, cov_matrix, num_portfolios_slider, risk_free_rate, constraints, bounds)
    except Exception as e:
        st.error(f"An error occurred during portfolio optimization: {e}")
        results_df = pd.DataFrame() # Ensure it's an empty df on error


    if not results_df.empty:
        fig_frontier = plot_efficient_frontier(results_df, risk_free_rate)
        st.plotly_chart(fig_frontier, use_container_width=True)

        # --- Display Optimal Portfolios ---
        st.header("Optimal Portfolio Details")
        col1, col2 = st.columns(2)
        min_vol_stats, min_vol_context = pd.Series(), ""
        max_sharpe_stats, max_sharpe_context = pd.Series(), ""

        with col1:
            min_vol_stats, min_vol_context = display_portfolio_summary(results_df, "Min Volatility")
        with col2:
            max_sharpe_stats, max_sharpe_context = display_portfolio_summary(results_df, "Max Sharpe")

        # --- Bootstrapping Simulation (Optional) ---
        st.header("Bootstrapping Simulation")
        selected_portfolio_for_sim = st.radio(
            "Select portfolio for simulation:",
            ('Max Sharpe', 'Min Volatility'), horizontal=True, key="sim_portfolio_choice"
        )

        num_sims = st.slider("Number of Bootstrap Simulations:", 500, 5000, 1000, key="num_sims")
        sim_years = st.number_input("Simulation Horizon (Years):", 1, 10, 1, key="sim_years")

        if st.button("Run Simulation", key="run_sim_button"):
            if selected_portfolio_for_sim == 'Max Sharpe':
                weights_for_sim = results_df.loc['Max Sharpe'].drop(['Return', 'Volatility', 'Sharpe Ratio']).values
            else: # Min Volatility
                weights_for_sim = results_df.loc['Min Volatility'].drop(['Return', 'Volatility', 'Sharpe Ratio']).values

            simulated_end_values, fig_sim_dist = run_bootstrap_simulation(returns, weights_for_sim, num_simulations=num_sims, sim_years=sim_years)

            if simulated_end_values:
                fig_sim_hist = plot_simulation_histogram(simulated_end_values, num_sims, sim_years)
                st.plotly_chart(fig_sim_hist, use_container_width=True)
                # st.plotly_chart(fig_sim_dist, use_container_width=True) # Optional: Show daily return distribution
                # Calculate and display summary stats of simulation
                final_returns_pct = [(val - 1) * 100 for val in simulated_end_values]
                st.metric("Mean Simulated Return", f"{np.mean(final_returns_pct):.2f}%")
                st.metric("Median Simulated Return", f"{np.median(final_returns_pct):.2f}%")
                st.metric("5th Percentile Return", f"{np.percentile(final_returns_pct, 5):.2f}%")
                st.metric("95th Percentile Return", f"{np.percentile(final_returns_pct, 95):.2f}%")
            else:
                st.warning("Simulation could not be completed.")


        # --- Gemini AI Analysis Panel ---
        st.sidebar.markdown("---")
        st.sidebar.subheader("🤖 Gemini AI Analysis")
        if st.session_state.get('gemini_api_key') and st.session_state.get('gemini_model'):
             prompt_options = [
                 "Explain the Efficient Frontier chart. What does it signify?",
                 f"Analyze the characteristics of the calculated 'Max Sharpe Ratio' portfolio. What type of investor might prefer this?",
                 f"Analyze the characteristics of the calculated 'Minimum Volatility' portfolio. What type of investor might prefer this?",
                 "Compare the 'Max Sharpe' and 'Min Volatility' portfolios. What are the key trade-offs?",
                 # Add prompts related to bootstrap results if simulation was run
             ]
             chosen_prompt = st.sidebar.selectbox("Select an analysis prompt:", prompt_options, key="po_gemini_prompt")

             if st.sidebar.button("Ask Gemini", key="po_gemini_button"):
                 # Combine context from the optimal portfolios
                 full_context = f"Portfolio Optimization Results:\n{min_vol_context}\n\n{max_sharpe_context}"
                 # Optionally add context from bootstrap if run
                 # if 'final_returns_pct' in locals():
                 #     full_context += f"\n\nBootstrap Simulation ({selected_portfolio_for_sim}) Summary:\nMean Return: {np.mean(final_returns_pct):.2f}%, Median: {np.median(final_returns_pct):.2f}%, 5th Perc: {np.percentile(final_returns_pct, 5):.2f}%, 95th Perc: {np.percentile(final_returns_pct, 95):.2f}%"

                 analysis = get_gemini_analysis(chosen_prompt, full_context)
                 with st.expander("💡 Gemini AI Insights", expanded=True):
                      st.markdown(analysis)
        else:
             st.sidebar.warning("Configure Gemini API Key in Settings to enable AI analysis.")

    else:
        st.warning("Could not generate Efficient Frontier. Check data and optimization parameters.")


if __name__ == "__main__":
    # Minimal setup for direct running
    if 'portfolio_tickers' not in st.session_state: st.session_state.portfolio_tickers = ['AAPL', 'MSFT', 'GOOG'] # Example
    if 'start_date' not in st.session_state: st.session_state.start_date = pd.to_datetime('2022-01-01')
    if 'end_date' not in st.session_state: st.session_state.end_date = pd.to_datetime('today')
    if 'risk_free_rate' not in st.session_state: st.session_state.risk_free_rate = 0.02
    if 'gemini_api_key' not in st.session_state: st.session_state.gemini_api_key = None
    if 'gemini_model' not in st.session_state: st.session_state.gemini_model = None
    show()