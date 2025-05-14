"""
Bokeh plot generation helpers for portfolio optimization results.
"""
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import ColorBar, LinearColorMapper, BasicTicker
from bokeh.transform import linear_cmap
from bokeh.palettes import Viridis256


def efficient_frontier_plot(df, optimal):
    """
    Create efficient frontier scatter plot with Sharpe ratio coloring and optimal points highlighted.
    Args:
        df (pd.DataFrame): Portfolio metrics DataFrame
        optimal (dict): Dict of optimal portfolios
    Returns:
        bokeh.plotting.Figure
    """
    mapper = linear_cmap(field_name='Sharpe', palette=Viridis256,
                        low=df['Sharpe'].min(), high=df['Sharpe'].max())
    p = figure(title="Efficient Frontier", x_axis_label="Risk (Volatility)", y_axis_label="Return",
               width=600, height=400, tools="pan,wheel_zoom,box_zoom,reset,save")
    p.scatter('Risk', 'Return', source=df, color=mapper, size=6, legend_label="Portfolios", alpha=0.6)

    # Highlight optimal portfolios
    for label, color in zip(['max_sharpe', 'min_variance', 'max_return'], ['red', 'blue', 'green']):
        pt = optimal[label]
        p.scatter([pt['Risk']], [pt['Return']], color=color, size=16, marker="star",
                  legend_label=label.replace('_', ' ').title())

    color_bar = ColorBar(color_mapper=mapper['transform'], ticker=BasicTicker(), label_standoff=12, location=(0,0))
    p.add_layout(color_bar, 'right')
    p.legend.click_policy = "hide"
    return p

from bokeh.transform import cumsum
from math import pi
from bokeh.palettes import Category20
from bokeh.models import ColumnDataSource

def weights_pie_chart(weights_dict, asset_names, label, width=600):
    """
    Create a pie chart of asset weights for a given optimal portfolio.
    Args:
        weights_dict (dict): Dict of weights for a portfolio
        asset_names (list): List of asset names
        label (str): Title label for the chart
        width (int): Width of the chart in pixels
    Returns:
        bokeh.plotting.Figure
    """
    weights = [weights_dict[name] for name in asset_names]
    
    # Fix for color palette selection based on number of assets
    num_assets = len(asset_names)
    if num_assets <= 10:
        from bokeh.palettes import Category10
        colors = Category10[max(3, num_assets)][:num_assets]  # Category10 has entries for 3-10
    else:
        from bokeh.palettes import Category20
        colors = Category20[min(20, num_assets)] if num_assets <= 20 else Category20[20] * (num_assets // 20 + 1)
    
    data = {
        'asset': asset_names,
        'weight': weights,
        'angle': [w * 2 * pi for w in weights],
        'color': colors
    }
    source = ColumnDataSource(data)
    p = figure(height=400, width=width, title=f"{label} Portfolio Weights (Pie Chart)", toolbar_location=None,
               tools="hover", tooltips="@asset: @weight{0.00%}", x_range=(-0.5, 1.0))
    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='asset', source=source)
    p.axis.visible = False
    p.grid.grid_line_color = None
    return p


def plot_price_history(df, optimal=None):
    """
    Plot the historical price series for each asset and the optimal portfolio.
    
    Args:
        df (pd.DataFrame): Price DataFrame with dates as index and assets as columns
        optimal (dict, optional): Dict of optimal portfolios with weights
    
    Returns:
        bokeh.plotting.Figure: The price history chart
    """
    import pandas as pd
    from bokeh.plotting import figure
    from bokeh.palettes import Category10
    from bokeh.models import ColumnDataSource, HoverTool
    
    p = figure(title="Asset Price History", x_axis_label="Date", y_axis_label="Price",
               width=800, height=300, x_axis_type='datetime', tools="pan,wheel_zoom,box_zoom,reset,save")
    
    # Only plot asset columns (exclude metrics)
    asset_names = [name for name in df.columns if name not in ['Return', 'Risk', 'Sharpe']]
    palette = Category10[10] if len(asset_names) <= 10 else Category10[10] * (len(asset_names) // 10 + 1)
    
    # Add hover tool for better user experience
    hover = HoverTool(
        tooltips=[
            ("Date", "@date{%F}"),
            ("Price", "@price{0.00}"),
            ("Asset", "$name")
        ],
        formatters={"@date": "datetime"},
        mode="vline"
    )
    p.add_tools(hover)
    
    # Plot individual assets
    for i, asset in enumerate(asset_names):
        if asset in df:
            source = ColumnDataSource(data={
                'date': df.index,
                'price': df[asset]
            })
            p.line('date', 'price', source=source, legend_label=asset, 
                   color=palette[i], line_width=1.5, name=asset)
    
    # Add Max Sharpe portfolio line if optimal weights are provided
    if optimal and 'max_sharpe' in optimal and len(df) > 0:
        # Extract weights for max Sharpe portfolio
        weights = {k: v for k, v in optimal['max_sharpe'].items() 
                  if k in asset_names and k in df.columns}
        
        if weights:
            # Normalize weights to ensure they sum to 1
            weight_sum = sum(weights.values())
            if weight_sum > 0:
                weights = {k: v/weight_sum for k, v in weights.items()}
                
                # Calculate portfolio value over time (starting with $1)
                # First, ensure all assets have data for all dates to prevent issues
                assets_data = {}
                for asset, weight in weights.items():
                    if asset in df.columns:
                        assets_data[asset] = df[asset]
                
                # Create a portfolio value series using the weighted returns
                # Initialize at $1 (100%)
                portfolio_values = pd.Series(1.0, index=df.index)
                
                # Calculate daily returns for each asset
                returns_df = pd.DataFrame(index=df.index)
                for asset in assets_data:
                    returns_df[asset] = assets_data[asset].pct_change().fillna(0)
                
                # Calculate the weighted daily returns of the portfolio
                for i in range(1, len(portfolio_values)):
                    daily_return = 0
                    for asset, weight in weights.items():
                        if asset in returns_df.columns:
                            daily_return += returns_df[asset].iloc[i] * weight
                    
                    # Update portfolio value
                    portfolio_values.iloc[i] = portfolio_values.iloc[i-1] * (1 + daily_return)
                
                # Create source for the portfolio line
                source = ColumnDataSource(data={
                    'date': df.index,
                    'price': portfolio_values
                })
                
                # Add the max Sharpe portfolio line with distinct styling
                p.line('date', 'price', source=source, legend_label='Max Sharpe Portfolio',
                       color='red', line_width=3, line_dash='solid', name='Max Sharpe Portfolio')
    
    # Configure legend
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    p.legend.background_fill_alpha = 0.7
    
    return p


def combined_layout(df, optimal, price_data=None):
    """
    Combine all plots into a 2x2 grid layout for output.
    Col 1: Efficient frontier
    Col 2: Price history line chart on top, three pie charts horizontally below
    
    Args:
        df (pd.DataFrame): Portfolio metrics DataFrame
        optimal (dict): Dict of optimal portfolios
        price_data (pd.DataFrame): Original price DataFrame
    
    Returns:
        bokeh.layouts.LayoutDOM: Combined layout of all plots
    """
    from bokeh.layouts import row, column
    
    # Extract asset names (excluding metrics columns)
    asset_names = [name for name in df.columns if name not in ['Return', 'Risk', 'Sharpe']]
    
    # Create efficient frontier plot
    frontier = efficient_frontier_plot(df, optimal)
    
    # Create price history chart with max Sharpe portfolio line
    price_chart = plot_price_history(price_data if price_data is not None else df, optimal=optimal)
    
    # Create pie charts for optimal portfolios
    pie_chart_width = 266  # 800px (line chart width) / 3
    pie_max_sharpe = weights_pie_chart(optimal['max_sharpe'], asset_names, 'Max Sharpe', width=pie_chart_width)
    pie_min_var = weights_pie_chart(optimal['min_variance'], asset_names, 'Min Variance', width=pie_chart_width)
    pie_max_return = weights_pie_chart(optimal['max_return'], asset_names, 'Max Return', width=pie_chart_width)
    
    # Arrange pie charts in a row
    pie_row = row(pie_max_sharpe, pie_min_var, pie_max_return)
    
    # Arrange price chart and pie charts in a column
    right_column = column(price_chart, pie_row)
    
    # Return the final layout
    return row(frontier, right_column)
