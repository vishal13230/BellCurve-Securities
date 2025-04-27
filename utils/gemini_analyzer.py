import streamlit as st
import google.generativeai as genai
import time # For potential retries or delays

# --- Gemini Configuration ---
@st.cache_resource # Cache the model resource
def configure_gemini(api_key):
    """Configures the Gemini API and returns the model."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') # Or another suitable model
        return model
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}. Please check your API key in Settings.")
        return None

def get_gemini_analysis(prompt, context_data=""):
    """
    Gets analysis from Gemini, handling potential errors.

    Args:
        prompt (str): The specific question or instruction for Gemini.
        context_data (str): Optional string containing data (metrics, signals) for context.

    Returns:
        str: The generated analysis from Gemini or an error message.
    """
    if 'gemini_model' not in st.session_state or st.session_state.gemini_model is None:
        # Try to re-initialize if API key is available
        if st.session_state.get('gemini_api_key'):
             st.session_state.gemini_model = configure_gemini(st.session_state.gemini_api_key)
             if st.session_state.gemini_model is None:
                  return "Gemini model not configured. Please set your API key in Settings."
        else:
            return "Gemini API key not set. Please configure it in Settings."

    model = st.session_state.gemini_model
    full_prompt = f"{context_data}\n\n---\n\n{prompt}"

    try:
        # Add a spinner while waiting for the response
        with st.spinner("🤖 Gemini is thinking..."):
            response = model.generate_content(full_prompt)
            # Handle potential safety blocks or empty responses
            if not response.parts:
                 # Check candidate for block reason if possible
                 try:
                      block_reason = response.candidates[0].finish_reason
                      safety_ratings = response.candidates[0].safety_ratings
                      return f"Analysis blocked by Gemini. Reason: {block_reason}. Ratings: {safety_ratings}"
                 except Exception:
                      return "Gemini returned an empty response. The prompt might have been blocked."

            return response.text # Or response.parts[0].text depending on API version/model

    except Exception as e:
        st.error(f"An error occurred while querying Gemini: {e}")
        # Simple retry logic (optional)
        # try:
        #     time.sleep(2)
        #     response = model.generate_content(full_prompt)
        #     return response.text
        # except Exception as e2:
        #      st.error(f"Retry failed: {e2}")
        #      return f"Error contacting Gemini: {e2}"
        return f"Error contacting Gemini: {e}"