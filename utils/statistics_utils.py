import numpy as np
import pandas as pd
from scipy.stats import norm, skew, kurtosis
import plotly.figure_factory as ff
import plotly.graph_objects as go

def calculate_returns(data):
    """Calculates daily percentage returns."""
    if isinstance(data, pd.Series):
        return data.pct_change().dropna()
    elif isinstance(data, pd.DataFrame):
        return data.pct_change().dropna()
    else:
        raise ValueError("Input data must be a pandas Series or DataFrame")

def calculate_statistics(returns):
    """Calculates key statistics for a series of returns."""
    if returns.empty:
        return {}
    stats = {
        'Mean Return (Ann)': returns.mean() * 252,
        'Volatility (Ann)': returns.std() * np.sqrt(252),
        'Median Return': returns.median(),
        'Variance': returns.var(),
        'Skewness': skew(returns),
        'Kurtosis': kurtosis(returns) # Fisher's definition (normal=0)
    }
    return stats

def calculate_sharpe_ratio(returns, risk_free_rate):
    """Calculates the annualized Sharpe Ratio."""
    if returns.empty or returns.std() == 0:
        return 0
    excess_returns = returns.mean() - (risk_free_rate / 252) # Daily risk-free rate
    sharpe = (excess_returns / returns.std()) * np.sqrt(252) # Annualize
    return sharpe

def plot_return_distribution(returns, ticker_name):
    """Plots the distribution of returns using Plotly."""
    if returns.empty:
        return go.Figure()

    # Create distribution plot with histogram and kernel density estimate (KDE)
    fig = ff.create_distplot(
        [returns.dropna()],
        group_labels=[f'{ticker_name} Daily Returns'],
        bin_size=0.005,  # Adjust bin size as needed
        show_hist=True,
        show_rug=False,
        show_curve=True
    )

    # Add vertical line for mean return
    mean_return = returns.mean()
    fig.add_vline(x=mean_return, line_dash="dash", line_color="red", annotation_text=f"Mean: {mean_return:.4f}")

    fig.update_layout(
        title=f'Distribution of Daily Returns for {ticker_name}',
        xaxis_title='Daily Return',
        yaxis_title='Density',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig