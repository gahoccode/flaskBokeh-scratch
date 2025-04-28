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
    Returns:
        bokeh.plotting.Figure
    """
    weights = [weights_dict[name] for name in asset_names]
    data = {
        'asset': asset_names,
        'weight': weights,
        'angle': [w * 2 * pi for w in weights],
        'color': Category20[len(asset_names)] if len(asset_names) <= 20 else Category20[20] * (len(asset_names) // 20 + 1)
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


def plot_price_history(df):
    """
    Plot the historical price series for each asset.
    Args:
        df (pd.DataFrame): Portfolio metrics DataFrame or price DataFrame
    Returns:
        bokeh.plotting.Figure
    """
    from bokeh.plotting import figure
    p = figure(title="Asset Price History", x_axis_label="Date", y_axis_label="Price",
               width=800, height=300, x_axis_type='auto')
    # Only plot asset columns (exclude metrics)
    asset_names = [name for name in df.columns if name not in ['Return', 'Risk', 'Sharpe']]
    from bokeh.palettes import Category10
    palette = Category10[10] if len(asset_names) <= 10 else Category10[10] * (len(asset_names) // 10 + 1)
    for i, asset in enumerate(asset_names):
        if asset in df:
            p.line(df.index, df[asset], legend_label=asset, color=palette[i])
    p.legend.click_policy = "hide"
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
        bokeh.layouts.LayoutDOM
    """
    from bokeh.layouts import row, column
    asset_names = [name for name in df.columns if name not in ['Return', 'Risk', 'Sharpe']]
    frontier = efficient_frontier_plot(df, optimal)
    price_chart = plot_price_history(price_data if price_data is not None else df)
    pie_chart_width = 266  # 800px (line chart width) / 3
    pie_max_sharpe = weights_pie_chart(optimal['max_sharpe'], asset_names, 'Max Sharpe', width=pie_chart_width)
    pie_min_var = weights_pie_chart(optimal['min_variance'], asset_names, 'Min Variance', width=pie_chart_width)
    pie_max_return = weights_pie_chart(optimal['max_return'], asset_names, 'Max Return', width=pie_chart_width)
    pie_row = row(pie_max_sharpe, pie_min_var, pie_max_return)
    right_column = column(price_chart, pie_row)
    return row(frontier, right_column)
