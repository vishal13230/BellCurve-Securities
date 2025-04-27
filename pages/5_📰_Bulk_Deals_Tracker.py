import streamlit as st
from utils.bulk_deals_scraper import get_bulk_deals_data # Placeholder
from components.bulk_deals_table import display_bulk_deals # Placeholder display
from utils.gemini_analyzer import get_gemini_analysis

def show():
    st.title("📰 Bulk & Block Deals Tracker")
    st.markdown("Monitor recent significant market transactions.")
    st.warning("Note: Accessing reliable, real-time bulk/block deal data often requires paid APIs or careful web scraping (check terms of service). This section uses placeholder data.", icon="⚠️")

    # Fetch Data (from placeholder function)
    deals_df = get_bulk_deals_data()

    # Display Data
    deals_context = display_bulk_deals(deals_df)

    # --- Gemini AI Analysis Panel ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 Gemini AI Analysis")
    if st.session_state.get('gemini_api_key') and st.session_state.get('gemini_model') and deals_context:
         prompt_options = [
             "Analyze the potential impact of the largest recent bulk/block deals listed.",
             "Are there any notable patterns or trends in the recent bulk deal activity shown?",
             "Identify any deals involving well-known institutions or investors from the list.",
         ]
         chosen_prompt = st.sidebar.selectbox("Select an analysis prompt:", prompt_options, key="bd_gemini_prompt")

         if st.sidebar.button("Ask Gemini", key="bd_gemini_button"):
             analysis = get_gemini_analysis(chosen_prompt, deals_context)
             with st.expander("💡 Gemini AI Insights", expanded=True):
                  st.markdown(analysis)
    elif not deals_context:
         st.sidebar.info("No deal data to analyze.")
    else:
         st.sidebar.warning("Configure Gemini API Key in Settings to enable AI analysis.")


if __name__ == "__main__":
    # Minimal setup for direct running
    if 'gemini_api_key' not in st.session_state: st.session_state.gemini_api_key = None
    if 'gemini_model' not in st.session_state: st.session_state.gemini_model = None
    show()