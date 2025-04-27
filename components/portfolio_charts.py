import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def plot_efficient_frontier(results_df, risk_free_rate):
    """Plots the Efficient Frontier and highlights optimal portfolios."""
    if results_df.empty:
        st.warning("No portfolio results to plot.")
        return go.Figure()

    fig = go.Figure()

    # Scatter plot for all generated portfolios on the frontier
    fig.add_trace(go.Scatter(
        x=results_df['Volatility'],
        y=results_df['Return'],
        mode='markers',
        marker=dict(
            size=8,
            color=results_df['Sharpe Ratio'], # Color by Sharpe Ratio
            colorscale='YlGnBu', # Choose a colorscale
            showscale=True,
            colorbar=dict(title='Sharpe Ratio')
        ),
        text=[f"Sharpe: {sr:.2f}<br>Return: {r:.2%}<br>Vol: {v:.2%}"
              for sr, r, v in zip(results_df['Sharpe Ratio'], results_df['Return'], results_df['Volatility'])],
        hoverinfo='text',
        name='Efficient Frontier Portfolios'
    ))

    # Highlight Min Volatility Portfolio
    min_vol_portfolio = results_df.loc['Min Volatility']
    fig.add_trace(go.Scatter(
        x=[min_vol_portfolio['Volatility']],
        y=[min_vol_portfolio['Return']],
        mode='markers',
        marker=dict(color='red', size=12, symbol='star'),
        name=f"Min Volatility (Vol: {min_vol_portfolio['Volatility']:.2%}, Ret: {min_vol_portfolio['Return']:.2%})"
    ))

    # Highlight Max Sharpe Ratio Portfolio
    max_sharpe_portfolio = results_df.loc['Max Sharpe']
    fig.add_trace(go.Scatter(
        x=[max_sharpe_portfolio['Volatility']],
        y=[max_sharpe_portfolio['Return']],
        mode='markers',
        marker=dict(color='green', size=12, symbol='star'),
        name=f"Max Sharpe (Vol: {max_sharpe_portfolio['Volatility']:.2%}, Ret: {max_sharpe_portfolio['Return']:.2%})"
    ))

    # (Optional) Add Capital Allocation Line (CAL)
    # cal_x = [0, max_sharpe_portfolio['Volatility'], max_sharpe_portfolio['Volatility'] * 1.5]
    # cal_y = [risk_free_rate, max_sharpe_portfolio['Return'], risk_free_rate + (max_sharpe_portfolio['Return'] - risk_free_rate) * 1.5]
    # fig.add_trace(go.Scatter(
    #     x=cal_x, y=cal_y, mode='lines', line=dict(dash='dash', color='purple'), name='Capital Allocation Line'
    # ))


    fig.update_layout(
        title='Efficient Frontier',
        xaxis_title='Annualized Volatility (Standard Deviation)',
        yaxis_title='Annualized Return',
        yaxis_tickformat='.1%',
        xaxis_tickformat='.1%',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        coloraxis_colorbar=dict(title="Sharpe Ratio")
    )
    return fig


def display_portfolio_summary(portfolio_results, portfolio_name):
     """Displays the stats and weights for a specific optimal portfolio."""
     if portfolio_name not in portfolio_results.index:
         st.warning(f"Portfolio '{portfolio_name}' not found in results.")
         return pd.Series(), "" # Return empty series and context

     stats = portfolio_results.loc[portfolio_name, ['Return', 'Volatility', 'Sharpe Ratio']]
     weights = portfolio_results.loc[portfolio_name].drop(['Return', 'Volatility', 'Sharpe Ratio'])
     weights = weights[weights > 0.0001] # Filter out negligible weights for display

     st.subheader(f"Optimal Portfolio: {portfolio_name}")
     col1, col2, col3 = st.columns(3)
     col1.metric("Expected Annual Return", f"{stats['Return']:.2%}")
     col2.metric("Annual Volatility", f"{stats['Volatility']:.2%}")
     col3.metric("Sharpe Ratio", f"{stats['Sharpe Ratio']:.2f}")

     st.subheader("Optimal Weights")
     # Use a bar chart or pie chart for weights
     fig_weights = go.Figure(data=[go.Pie(labels=weights.index, values=weights.values, hole=.3,
                                         textinfo='label+percent', pull=[0.05] * len(weights))])
     fig_weights.update_layout(title_text='Portfolio Allocation', showlegend=False)
     st.plotly_chart(fig_weights, use_container_width=True)

     st.dataframe(weights.map('{:.2%}'.format), use_container_width=True) # Show weights in a table too

     # Prepare context for Gemini
     weights_str = "\n".join([f"- {ticker}: {weight:.2%}" for ticker, weight in weights.items()])
     portfolio_context = f"""
     Optimized Portfolio ({portfolio_name}):
     Expected Annual Return: {stats['Return']:.2%}
     Annual Volatility: {stats['Volatility']:.2%}
     Sharpe Ratio: {stats['Sharpe Ratio']:.2f}
     Optimal Weights:
     {weights_str}
     """
     return stats, portfolio_context