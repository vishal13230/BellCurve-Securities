import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Technical Indicator Calculations (should ideally be in utils) ---
def calculate_sma(data, window):
    return data.rolling(window=window).mean()

def calculate_ema(data, span):
    return data.ewm(span=span, adjust=False).mean()

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, span1=12, span2=26, signal=9):
    ema1 = calculate_ema(data, span1)
    ema2 = calculate_ema(data, span2)
    macd_line = ema1 - ema2
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    sma = calculate_sma(data, window)
    std_dev = data.rolling(window=window).std()
    upper_band = sma + (std_dev * num_std_dev)
    lower_band = sma - (std_dev * num_std_dev)
    return upper_band, sma, lower_band

# --- Plotting Functions ---
def plot_technical_analysis(ticker, df_ticker_price, df_ticker_volume):
    """Plots Price, Volume, MA, Bollinger Bands, RSI, MACD."""
    if df_ticker_price.empty:
        st.warning(f"No price data to plot for {ticker}.")
        return go.Figure(), "" # Return empty figure and context

    # Create figure with subplots
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                       vertical_spacing=0.03,
                       row_heights=[0.5, 0.1, 0.2, 0.2]) # Adjust heights as needed

    # 1. Candlestick with Bollinger Bands and MAs
    # Calculate Bollinger Bands
    upper_band, middle_band, lower_band = calculate_bollinger_bands(df_ticker_price)
    # Calculate MAs
    sma50 = calculate_sma(df_ticker_price, 50)
    sma200 = calculate_sma(df_ticker_price, 200)

    # Candlestick (Requires OHLC data - get_stock_data needs modification)
    # For now, using line plot of Adj Close
    fig.add_trace(go.Scatter(x=df_ticker_price.index, y=df_ticker_price, mode='lines', name='Adj Close', line=dict(color='blue')), row=1, col=1)

    # Bollinger Bands
    fig.add_trace(go.Scatter(x=upper_band.index, y=upper_band, mode='lines', line=dict(width=1, color='rgba(152,0,0,0.3)'), name='Upper Band'), row=1, col=1)
    fig.add_trace(go.Scatter(x=middle_band.index, y=middle_band, mode='lines', line=dict(width=1, dash='dash', color='rgba(152,0,0,0.5)'), name=f'SMA {20}'), row=1, col=1)
    fig.add_trace(go.Scatter(x=lower_band.index, y=lower_band, mode='lines', line=dict(width=1, color='rgba(152,0,0,0.3)'), name='Lower Band', fill='tonexty', fillcolor='rgba(152,0,0,0.1)'), row=1, col=1)

    # Moving Averages
    fig.add_trace(go.Scatter(x=sma50.index, y=sma50, mode='lines', name='SMA 50', line=dict(color='orange')), row=1, col=1)
    fig.add_trace(go.Scatter(x=sma200.index, y=sma200, mode='lines', name='SMA 200', line=dict(color='purple')), row=1, col=1)

    # 2. Volume
    if not df_ticker_volume.empty:
         fig.add_trace(go.Bar(x=df_ticker_volume.index, y=df_ticker_volume, name='Volume', marker_color='grey'), row=2, col=1)

    # 3. RSI
    rsi = calculate_rsi(df_ticker_price)
    fig.add_trace(go.Scatter(x=rsi.index, y=rsi, mode='lines', name='RSI', line=dict(color='green')), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="blue", row=3, col=1)

    # 4. MACD
    macd_line, signal_line, histogram = calculate_macd(df_ticker_price)
    fig.add_trace(go.Scatter(x=macd_line.index, y=macd_line, mode='lines', name='MACD Line', line=dict(color='black')), row=4, col=1)
    fig.add_trace(go.Scatter(x=signal_line.index, y=signal_line, mode='lines', name='Signal Line', line=dict(color='red')), row=4, col=1)
    # Color histogram bars based on positive/negative
    colors = ['green' if val >= 0 else 'red' for val in histogram]
    fig.add_trace(go.Bar(x=histogram.index, y=histogram, name='MACD Hist', marker_color=colors), row=4, col=1)
    fig.add_hline(y=0, line_dash="solid", line_color="grey", row=4, col=1)


    # Update layout
    fig.update_layout(
        title=f'Technical Analysis for {ticker}',
        height=800,
        xaxis_rangeslider_visible=False, # Hide range slider for main plot
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
        yaxis1_title="Price",
        yaxis2_title="Volume",
        yaxis3_title="RSI",
        yaxis4_title="MACD"
    )
    # Disable zoom on volume/indicator subplots if desired
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1) # Set RSI range
    fig.update_yaxes(title_text="MACD", row=4, col=1)


    # --- Prepare context for Gemini ---
    # Get latest values
    latest_price = df_ticker_price.iloc[-1] if not df_ticker_price.empty else 'N/A'
    latest_rsi = rsi.iloc[-1] if not rsi.empty else 'N/A'
    latest_macd = macd_line.iloc[-1] if not macd_line.empty else 'N/A'
    latest_signal = signal_line.iloc[-1] if not signal_line.empty else 'N/A'
    latest_upper = upper_band.iloc[-1] if not upper_band.empty else 'N/A'
    latest_lower = lower_band.iloc[-1] if not lower_band.empty else 'N/A'
    latest_sma50 = sma50.iloc[-1] if not sma50.empty else 'N/A'
    latest_sma200 = sma200.iloc[-1] if not sma200.empty else 'N/A'

    technical_context = f"""
    Technical Indicators for {ticker} (Latest Values):
    Price: {latest_price:.2f}
    SMA50: {latest_sma50:.2f}
    SMA200: {latest_sma200:.2f}
    Bollinger Bands: Lower={latest_lower:.2f}, Upper={latest_upper:.2f}
    RSI(14): {latest_rsi:.2f}
    MACD Line: {latest_macd:.4f}
    Signal Line: {latest_signal:.4f}
    MACD Histogram: {histogram.iloc[-1]:.4f}
    Volume (latest): {df_ticker_volume.iloc[-1] if not df_ticker_volume.empty else 'N/A'}

    Price relative to MAs: {'Above SMA50' if latest_price > latest_sma50 else 'Below SMA50'}, {'Above SMA200' if latest_price > latest_sma200 else 'Below SMA200'}
    Price relative to Bollinger Bands: {'Near Upper' if latest_price > upper_band.iloc[-2] else ('Near Lower' if latest_price < lower_band.iloc[-2] else 'Mid-Band')}
    RSI Level: {'Overbought (>70)' if latest_rsi > 70 else ('Oversold (<30)' if latest_rsi < 30 else 'Neutral')}
    MACD Signal: {'Bullish Crossover (MACD > Signal)' if latest_macd > latest_signal else ('Bearish Crossover (MACD < Signal)' if latest_macd < latest_signal else 'Neutral')}
    """

    return fig, technical_context