"""
Unit test for Bokeh HTML output saving and Flask serving compatibility.
"""
import os
import tempfile
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, save
from app.plots import combined_layout
import pytest

@pytest.fixture
def dummy_metrics_and_optimal():
    # Minimal dummy data
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

def test_bokeh_html_output_and_serve(dummy_metrics_and_optimal):
    df, optimal = dummy_metrics_and_optimal
    layout = combined_layout(df, optimal)
    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = os.path.join(tmpdir, "test_output.html")
        output_file(html_path, title="Test Portfolio Results")
        save(layout)
        assert os.path.exists(html_path)
        # Check that file is valid HTML and contains Bokeh script
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "<html" in content.lower()
            assert "bokeh" in content.lower()
            assert "<script" in content.lower()
        # Simulate Flask send_file usage (mimetype check)
        from mimetypes import guess_type
        mimetype, _ = guess_type(html_path)
        assert mimetype == "text/html"
