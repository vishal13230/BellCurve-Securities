import streamlit as st
from utils.gemini_analyzer import configure_gemini # Import the configuration function

def show():
    st.title("⚙️ Settings & Preferences")

    st.header("API Keys")
    st.warning("API keys are stored in session state and will be lost when the browser tab is closed unless explicitly saved elsewhere (not implemented here for security). Never hardcode API keys.")

    # --- Gemini API Key ---
    gemini_key_input = st.text_input(
        "Google Gemini API Key",
        type="password",
        value=st.session_state.get('gemini_api_key', ''),
        help="Get your key from Google AI Studio: https://aistudio.google.com/app/apikey"
    )
    if gemini_key_input:
        st.session_state['gemini_api_key'] = gemini_key_input
        # Attempt to configure Gemini immediately when the key is entered/changed
        try:
            st.session_state['gemini_model'] = configure_gemini(st.session_state['gemini_api_key'])
            if st.session_state['gemini_model']:
                st.success("Gemini API Key configured successfully.")
            else:
                # Error message is handled within configure_gemini
                pass
        except Exception as e:
            st.error(f"Failed to configure Gemini: {e}")
            st.session_state['gemini_model'] = None
    elif st.session_state.get('gemini_api_key'):
         # If key exists in session state but input is cleared, clear the model too
         st.session_state['gemini_api_key'] = None
         st.session_state['gemini_model'] = None
         st.info("Gemini API Key cleared.")


    # --- Other API Keys (Placeholder) ---
    # st.text_input("News API Key (Optional)", type="password", key="news_api_key")
    # st.text_input("Financial Data Provider API Key (Optional)", type="password", key="data_api_key")

    st.markdown("---")

    # --- General Settings ---
    st.header("Analysis Parameters")

    # Risk-Free Rate for Sharpe Ratio
    rf_rate = st.slider(
        "Risk-Free Rate (%) for Sharpe Ratio Calculation",
        min_value=0.0,
        max_value=10.0,
        value=st.session_state.get('risk_free_rate', 0.02) * 100, # Display as percentage
        step=0.1,
        format="%.1f%%",
        key="rf_rate_slider"
    )
    st.session_state['risk_free_rate'] = rf_rate / 100.0 # Store as decimal

    # --- Personalization (Placeholders) ---
    st.header("Personalization (Future Features)")
    st.selectbox("Preferred Sectors:", ["All", "Technology", "Healthcare", "Financials", "Energy", "Consumer Discretionary", "Industrials"], key="pref_sector", disabled=True)
    st.select_slider("Risk Appetite:", ["Conservative", "Moderate", "Aggressive"], value="Moderate", key="risk_appetite", disabled=True)

    st.markdown("---")

    # --- Saved Tickers (Simple Implementation using Session State) ---
    st.header("Manage Ticker Lists")
    st.write("Tickers managed here are used as defaults or suggestions.")

    st.subheader("Current Analysis Tickers")
    analysis_tickers_str = st.text_area(
        "Edit Analysis Tickers (comma-separated)",
        value=", ".join(st.session_state.get('tickers', [])),
        key="settings_analysis_tickers"
    )
    if st.button("Update Analysis Tickers", key="update_analysis"):
        st.session_state['tickers'] = [ticker.strip().upper() for ticker in analysis_tickers_str.split(',') if ticker.strip()]
        st.success("Analysis tickers updated.")
        st.rerun() # Rerun to reflect changes immediately

    st.subheader("Current Portfolio Tickers")
    portfolio_tickers_str = st.text_area(
        "Edit Portfolio Tickers (comma-separated)",
        value=", ".join(st.session_state.get('portfolio_tickers', [])),
        key="settings_portfolio_tickers"
    )
    if st.button("Update Portfolio Tickers", key="update_portfolio"):
        st.session_state['portfolio_tickers'] = [ticker.strip().upper() for ticker in portfolio_tickers_str.split(',') if ticker.strip()]
        st.success("Portfolio tickers updated.")
        st.rerun() # Rerun to reflect changes immediately

    # Add options for saving/loading settings locally if needed (more complex)

if __name__ == "__main__":
    # Minimal setup for direct running
    if 'risk_free_rate' not in st.session_state: st.session_state.risk_free_rate = 0.02
    if 'tickers' not in st.session_state: st.session_state.tickers = []
    if 'portfolio_tickers' not in st.session_state: st.session_state.portfolio_tickers = []
    if 'gemini_api_key' not in st.session_state: st.session_state.gemini_api_key = None
    if 'gemini_model' not in st.session_state: st.session_state.gemini_model = None
    show()