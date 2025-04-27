import streamlit as st
import pandas as pd
from utils.data_fetcher import get_stock_info, get_recommendations, get_earnings_history
from components.fundamental_metrics import display_fundamental_metrics, display_recommendations, display_earnings_history
from utils.gemini_analyzer import get_gemini_analysis

def show():
    st.title("📊 Fundamental Analysis")

    if not st.session_state.get('tickers'):
        st.warning("Please select at least one stock ticker in the sidebar.")
        return

    selected_ticker = st.selectbox("Select a stock for detailed analysis:", st.session_state.tickers)

    if selected_ticker:
        st.header(f"Analysis for: {selected_ticker}")

        # Fetch Data
        info = get_stock_info(selected_ticker)
        recommendations = get_recommendations(selected_ticker)
        earnings = get_earnings_history(selected_ticker)

        # Display Metrics
        fundamental_context = display_fundamental_metrics(selected_ticker, info)
        display_recommendations(selected_ticker, recommendations)
        display_earnings_history(selected_ticker, earnings)

        # --- Gemini AI Analysis Panel ---
        st.sidebar.markdown("---")
        st.sidebar.subheader("🤖 Gemini AI Analysis")
        if st.session_state.get('gemini_api_key') and st.session_state.get('gemini_model'):
             prompt_options = [
                 f"Analyze the key fundamental metrics for {selected_ticker}. Is it potentially overvalued or undervalued based on these metrics? What are the main risks and strengths?",
                 f"Summarize the business model and competitive position of {selected_ticker} based on its summary.",
                 f"What do the recent analyst recommendations suggest for {selected_ticker}?",
                 f"Explain the earnings history trend for {selected_ticker}."
             ]
             chosen_prompt = st.sidebar.selectbox("Select an analysis prompt:", prompt_options, key="fa_gemini_prompt")

             if st.sidebar.button("Ask Gemini", key="fa_gemini_button"):
                 # Combine context from displayed data
                 full_context = f"{fundamental_context}\n\nRecommendations Summary:\n{recommendations.head().to_string() if recommendations is not None else 'N/A'}\n\nEarnings Summary:\n{earnings.head().to_string() if earnings is not None else 'N/A'}"
                 analysis = get_gemini_analysis(chosen_prompt, full_context)
                 # Display analysis in a dedicated expander or area
                 with st.expander("💡 Gemini AI Insights", expanded=True):
                      st.markdown(analysis)
        else:
             st.sidebar.warning("Configure Gemini API Key in Settings to enable AI analysis.")


# Run the show function if the script is executed directly
if __name__ == "__main__":
    # Minimal setup for direct running (won't have sidebar selections)
    if 'tickers' not in st.session_state: st.session_state.tickers = ['AAPL', 'MSFT'] # Example
    if 'gemini_api_key' not in st.session_state: st.session_state.gemini_api_key = None
    if 'gemini_model' not in st.session_state: st.session_state.gemini_model = None
    show()