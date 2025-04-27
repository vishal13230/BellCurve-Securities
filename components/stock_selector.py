import streamlit as st

def render_stock_selector(context_key_suffix=""):
    """Renders the UI for selecting stocks for analysis (can be reused)."""
    st.subheader("Select Stocks")
    # Use a unique key based on the context if needed on multiple pages simultaneously
    input_key = f"stock_selector_input_{context_key_suffix}"
    session_key = 'tickers' # Use the global session state for FA/TA

    selected_tickers_str = st.text_input(
        "Enter Tickers (comma-separated)",
        value=", ".join(st.session_state.get(session_key, [])),
        key=input_key,
        help="Enter stock ticker symbols like AAPL, MSFT, GOOGL"
    )

    if selected_tickers_str:
        st.session_state[session_key] = [ticker.strip().upper() for ticker in selected_tickers_str.split(',') if ticker.strip()]
    else:
        st.session_state[session_key] = []

    st.caption(f"Currently selected for analysis: {', '.join(st.session_state[session_key]) if st.session_state[session_key] else 'None'}")
    return st.session_state[session_key]

def render_portfolio_selector(context_key_suffix="portfolio"):
     """Renders the UI for selecting stocks specifically for the portfolio."""
     st.subheader("Select Stocks for Portfolio")
     session_key = 'portfolio_tickers'

     # Suggest using tickers already selected for analysis
     available_tickers = st.session_state.get('tickers', [])
     default_selection = st.session_state.get(session_key, [])

     # Filter default selection to ensure they are valid based on available_tickers if needed,
     # or allow adding any ticker. Let's allow adding any for flexibility.
     all_possible_tickers = sorted(list(set(available_tickers + default_selection)))

     # Use multiselect for portfolio building
     selected_portfolio_tickers = st.multiselect(
         "Choose stocks from the list below, or type to add new ones:",
         options=all_possible_tickers, # Provide suggestions
         default=default_selection,
         key=f"portfolio_multiselect_{context_key_suffix}",
         # No free-form entry in standard multiselect, users need to add to global list first.
         # Alternative: Use text_input + parsing for full flexibility
     )

     # Allow adding new tickers directly to the portfolio list via text input
     new_portfolio_tickers_str = st.text_input(
         "Add more tickers (comma-separated)",
         key=f"portfolio_text_input_{context_key_suffix}",
         help="Add tickers specifically for the portfolio."
     )
     if new_portfolio_tickers_str:
         new_tickers = [ticker.strip().upper() for ticker in new_portfolio_tickers_str.split(',') if ticker.strip()]
         # Combine and remove duplicates
         st.session_state[session_key] = sorted(list(set(selected_portfolio_tickers + new_tickers)))
         # Clear the text input after adding
         st.rerun() # Rerun to update multiselect with new options if needed. Risky, use with care. Maybe update session state and let user see update?
         # Let's just update session state:
         # st.session_state[session_key] = sorted(list(set(selected_portfolio_tickers + new_tickers)))
     else:
          st.session_state[session_key] = selected_portfolio_tickers


     st.caption(f"Portfolio Tickers: {', '.join(st.session_state[session_key]) if st.session_state[session_key] else 'None'}")
     if len(st.session_state[session_key]) < 2:
          st.warning("Select at least two stocks for portfolio optimization.")
     return st.session_state[session_key]