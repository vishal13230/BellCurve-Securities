import streamlit as st
import pandas as pd

def display_bulk_deals(deals_df):
    """Displays the bulk deals data in a table."""
    st.subheader("Recent Bulk & Block Deals")
    if deals_df.empty:
        st.info("No recent bulk deal data found or source not implemented.")
        return "" # No context if no data

    # Optional: Add filtering options
    # Example: Filter by symbol
    # symbols = ['All'] + sorted(deals_df['Symbol'].unique())
    # selected_symbol = st.selectbox("Filter by Symbol:", symbols)
    # if selected_symbol != 'All':
    #     deals_df = deals_df[deals_df['Symbol'] == selected_symbol]

    st.dataframe(deals_df, use_container_width=True)

    # Prepare context for Gemini (e.g., summarize top deals)
    deals_context = f"""
    Recent Bulk/Block Deals Summary (Top 5 by Quantity):
    {deals_df.nlargest(5, 'Quantity').to_string()}
    """
    return deals_context