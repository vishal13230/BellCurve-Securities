import numpy as np
import pandas as pd
from scipy.optimize import minimize
from .statistics_utils import calculate_returns # Import from sibling module

def calculate_portfolio_performance(weights, mean_returns, cov_matrix):
    """Calculates portfolio return, volatility."""
    portfolio_return = np.sum(mean_returns * weights) * 252  # Annualized return
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252) # Annualized volatility
    return portfolio_return, portfolio_volatility

def calculate_neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
    """Calculates the negative Sharpe ratio (for minimization)."""
    p_return, p_volatility = calculate_portfolio_performance(weights, mean_returns, cov_matrix)
    if p_volatility == 0:
        return np.inf # Avoid division by zero; assign high value
    return -(p_return - risk_free_rate) / p_volatility

def calculate_portfolio_variance(weights, mean_returns, cov_matrix):
     """Calculates portfolio variance (or volatility for minimization)."""
     # We minimize volatility which is sqrt(variance), it yields the same weights.
     # Directly using variance avoids sqrt calculation in the optimizer loop.
     # return np.dot(weights.T, np.dot(cov_matrix, weights)) * 252 # Annualized Variance
     _, portfolio_volatility = calculate_portfolio_performance(weights, mean_returns, cov_matrix)
     return portfolio_volatility # Return volatility as it's more interpretable


def find_optimal_portfolio(opt_type, mean_returns, cov_matrix, risk_free_rate, num_assets, constraints, bounds):
    """Finds the optimal portfolio based on the optimization type."""
    if opt_type == 'max_sharpe':
        objective = calculate_neg_sharpe_ratio
        args = (mean_returns, cov_matrix, risk_free_rate)
    elif opt_type == 'min_volatility':
        objective = calculate_portfolio_variance
        args = (mean_returns, cov_matrix) # risk_free_rate not needed for min vol
    else:
        raise ValueError("Invalid optimization type specified.")

    # Initial guess (equal weights)
    init_guess = np.array(num_assets * [1. / num_assets])

    result = minimize(objective, init_guess, args=args, method='SLSQP', bounds=bounds, constraints=constraints)

    if not result.success:
        # Handle optimization failure (e.g., return None or raise an error)
        print(f"Optimization failed for {opt_type}: {result.message}")
        return None

    optimal_weights = result.x
    return optimal_weights

def generate_efficient_frontier(mean_returns, cov_matrix, num_portfolios, risk_free_rate, constraints, bounds):
    """Generates portfolios for the efficient frontier."""
    results = np.zeros((3 + len(mean_returns), num_portfolios)) # Return, Volatility, Sharpe, Weights...
    num_assets = len(mean_returns)
    init_guess = np.array(num_assets * [1. / num_assets])

    # Max Sharpe Portfolio (tangency portfolio)
    max_sharpe_weights = find_optimal_portfolio('max_sharpe', mean_returns, cov_matrix, risk_free_rate, num_assets, constraints, bounds)
    if max_sharpe_weights is None: return pd.DataFrame() # Optimization failed
    max_sharpe_ret, max_sharpe_vol = calculate_portfolio_performance(max_sharpe_weights, mean_returns, cov_matrix)
    max_sharpe_ratio = (max_sharpe_ret - risk_free_rate) / max_sharpe_vol

    # Min Volatility Portfolio
    min_vol_weights = find_optimal_portfolio('min_volatility', mean_returns, cov_matrix, risk_free_rate, num_assets, constraints, bounds)
    if min_vol_weights is None: return pd.DataFrame() # Optimization failed
    min_vol_ret, min_vol_vol = calculate_portfolio_performance(min_vol_weights, mean_returns, cov_matrix)
    min_vol_sharpe = (min_vol_ret - risk_free_rate) / min_vol_vol if min_vol_vol != 0 else 0

    # Store optimal portfolios
    results[0,0], results[1,0], results[2,0] = min_vol_ret, min_vol_vol, min_vol_sharpe
    results[3:,0] = min_vol_weights
    results[0,1], results[1,1], results[2,1] = max_sharpe_ret, max_sharpe_vol, max_sharpe_ratio
    results[3:,1] = max_sharpe_weights

    # Generate other frontier points by varying target return
    target_returns = np.linspace(min_vol_ret, max_sharpe_ret * 1.2, num_portfolios - 2) # Extend slightly beyond max sharpe return

    frontier_idx = 2
    for target_ret in target_returns:
        # Constraint: Portfolio return must equal the target return
        eff_constraints = (
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}, # Sum weights = 1
            {'type': 'eq', 'fun': lambda w: calculate_portfolio_performance(w, mean_returns, cov_matrix)[0] - target_ret} # Target return
        )
        # Minimize volatility for the target return
        result = minimize(calculate_portfolio_variance, init_guess, args=(mean_returns, cov_matrix), method='SLSQP', bounds=bounds, constraints=eff_constraints)

        if result.success:
            weights = result.x
            p_ret, p_vol = calculate_portfolio_performance(weights, mean_returns, cov_matrix)
            p_sharpe = (p_ret - risk_free_rate) / p_vol if p_vol != 0 else 0
            results[0,frontier_idx], results[1,frontier_idx], results[2,frontier_idx] = p_ret, p_vol, p_sharpe
            results[3:, frontier_idx] = weights
            frontier_idx += 1

    # Convert results to DataFrame
    columns = [f'Portfolio {i+1}' for i in range(frontier_idx)] # Only include successfully generated portfolios
    results_df = pd.DataFrame(results[:, :frontier_idx], index=['Return', 'Volatility', 'Sharpe Ratio'] + list(mean_returns.index), columns=columns)

    # Add specific labels for Min Vol and Max Sharpe portfolios for easy identification
    results_df = results_df.rename(columns={'Portfolio 1': 'Min Volatility', 'Portfolio 2': 'Max Sharpe'})

    return results_df.T # Transpose so portfolios are rows