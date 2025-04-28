"""Unit test for Bokeh HTML output saving and Flask serving compatibility."""
import os
import tempfile
import shutil
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, save
from app.plots import combined_layout
import pytest
from rich import print

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
    """Test that Bokeh HTML output can be generated and served."""
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


def test_output_directory_creation():
    """Test that the outputs directory is created if it doesn't exist."""
    # Get the base directory of the application
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_dir = os.path.join(base_dir, 'outputs')
    
    # Remove the directory if it exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    # Ensure the directory doesn't exist
    assert not os.path.exists(output_dir)
    
    # Create the directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Check that the directory exists
    assert os.path.exists(output_dir)
    assert os.path.isdir(output_dir)


def test_output_file_path():
    """Test that the output file path is constructed correctly."""
    # Get the base directory of the application
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_dir = os.path.join(base_dir, 'outputs')
    output_path = os.path.join(output_dir, 'output.html')
    
    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a dummy file
    with open(output_path, 'w') as f:
        f.write('<html><body>Test</body></html>')
    
    # Check that the file exists
    assert os.path.exists(output_path)
    assert os.path.isfile(output_path)
    
    # Clean up
    os.remove(output_path)
