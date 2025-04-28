"""
Unit tests for Bokeh visualization helpers (efficient frontier, weights bar, combined layout).
Covers figure creation, types, and minimal structure.
"""
import pandas as pd
import numpy as np
import pytest
from app.plots import efficient_frontier_plot, weights_bar_plot, combined_layout
from bokeh.plotting import figure
from bokeh.layouts import Column

FigureType = type(figure())

@pytest.fixture
def dummy_metrics_and_optimal():
    df = pd.DataFrame({
        'Return': np.random.rand(10),
        'Risk': np.random.rand(10),
        'Sharpe': np.random.rand(10),
        'AAA': np.random.rand(10),
        'BBB': np.random.rand(10)
    })
    optimal = {
        'max_sharpe': {'Risk': 0.2, 'Return': 0.1, 'AAA': 1.0, 'BBB': 0.0},
        'min_variance': {'Risk': 0.1, 'Return': 0.05, 'AAA': 0.5, 'BBB': 0.5},
        'max_return': {'Risk': 0.3, 'Return': 0.2, 'AAA': 0.7, 'BBB': 0.3}
    }
    return df, optimal

def test_efficient_frontier_plot(dummy_metrics_and_optimal):
    df, optimal = dummy_metrics_and_optimal
    fig = efficient_frontier_plot(df, optimal)
    assert isinstance(fig, FigureType)
    assert fig.title.text == "Efficient Frontier"
    assert fig.xaxis[0].axis_label == "Risk (Volatility)"
    assert fig.yaxis[0].axis_label == "Return"

def test_weights_bar_plot(dummy_metrics_and_optimal):
    df, optimal = dummy_metrics_and_optimal
    asset_names = [c for c in df.columns if c not in ['Return', 'Risk', 'Sharpe']]
    fig = weights_bar_plot(optimal, asset_names)
    assert isinstance(fig, FigureType)
    assert fig.title.text.startswith("Max Sharpe Portfolio Weights")
    assert fig.x_range.factors == asset_names

def test_combined_layout(dummy_metrics_and_optimal):
    df, optimal = dummy_metrics_and_optimal
    layout = combined_layout(df, optimal)
    assert isinstance(layout, Column)
    # Should contain two children: efficient frontier and weights bar
    assert len(layout.children) == 2
    assert all(isinstance(child, FigureType) for child in layout.children)
