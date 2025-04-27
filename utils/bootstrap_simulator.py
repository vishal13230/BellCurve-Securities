import numpy as np
import pandas as pd
from sklearn.utils import resample
import plotly.graph_objects as go
from .portfolio_optimizer import calculate_portfolio_performance # Import from sibling

def run_bootstrap_simulation(returns_df, weights, num_simulations=1000, sim_years=1):
    """
    Performs bootstrap simulation on portfolio returns.

    Args:
        returns_df (pd.DataFrame): DataFrame of daily returns for assets.
        weights (np.array): Portfolio weights.
        num_simulations (int): Number of bootstrap simulations to run.
        sim_years (int): Number of years to simulate forward for each path.

    Returns:
        list: A list of simulated portfolio ending values (or total returns).
        go.Figure: A Plotly figure showing the distribution of outcomes.
    """
    if returns_df.empty or len(weights) != returns_df.shape[1]:
        return [], go.Figure()

    sim_days = int(sim_years * 252) # Trading days per year
    simulated_end_values = []
    all_sim_returns = []

    for _ in range(num_simulations):
        # Bootstrap sampling of daily returns
        bootstrap_sample = resample(returns_df, n_samples=sim_days, replace=True)

        # Calculate portfolio return for this simulated path
        # Assuming starting value of 1, calculate cumulative return
        compounded_return = (1 + bootstrap_sample.dot(weights)).prod()
        simulated_end_values.append(compounded_return)
        all_sim_returns.extend(bootstrap_sample.dot(weights).tolist()) # Collect daily returns for distribution plot

    # Plot distribution of simulated daily portfolio returns
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=all_sim_returns, name='Simulated Daily Returns', nbinsx=50))
    fig.update_layout(
        title=f'Distribution of Simulated Daily Portfolio Returns ({num_simulations} paths, {sim_years} year(s))',
        xaxis_title='Simulated Daily Return',
        yaxis_title='Frequency'
    )

    return simulated_end_values, fig


def plot_simulation_histogram(simulated_end_values, num_simulations, sim_years):
     """Plots a histogram of the final simulated portfolio values."""
     if not simulated_end_values:
         return go.Figure()

     final_returns_pct = [(val - 1) * 100 for val in simulated_end_values] # Convert ending value to % return

     fig = go.Figure()
     fig.add_trace(go.Histogram(x=final_returns_pct, name='Simulated Outcomes', nbinsx=50))

     mean_outcome = np.mean(final_returns_pct)
     median_outcome = np.median(final_returns_pct)
     percentile_5 = np.percentile(final_returns_pct, 5)
     percentile_95 = np.percentile(final_returns_pct, 95)

     fig.add_vline(x=mean_outcome, line_dash="dash", line_color="red", annotation_text=f"Mean: {mean_outcome:.2f}%")
     fig.add_vline(x=median_outcome, line_dash="dash", line_color="green", annotation_text=f"Median: {median_outcome:.2f}%")
     fig.add_vline(x=percentile_5, line_dash="dot", line_color="orange", annotation_text=f"5th Perc: {percentile_5:.2f}%")
     fig.add_vline(x=percentile_95, line_dash="dot", line_color="purple", annotation_text=f"95th Perc: {percentile_95:.2f}%")


     fig.update_layout(
         title=f'Bootstrap Simulation Results ({num_simulations} paths, {sim_years} year(s))',
         xaxis_title=f'Simulated Total Return (%) over {sim_years} Year(s)',
         yaxis_title='Frequency',
         bargap=0.1
     )
     return fig