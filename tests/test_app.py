"""
Integration tests for Flask portfolio optimizer app.
Uses pytest and Flask test client.
"""
import pytest
from flask import session
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-key'
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_main_route_get(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Portfolio Optimization' in resp.data

def test_optimize_invalid_symbols(client):
    data = {
        'symbols': '',
        'start_date': '2024-01-01',
        'end_date': '2024-04-01',
        'num_portfolios': '5000',
        'risk_free_rate': '0.0',
    }
    resp = client.post('/optimize', data=data, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Please enter at least one stock symbol.' in resp.data

def test_optimize_invalid_dates(client):
    data = {
        'symbols': 'AAA',
        'start_date': '2024-05-01',
        'end_date': '2024-04-01',
        'num_portfolios': '5000',
        'risk_free_rate': '0.0',
    }
    resp = client.post('/optimize', data=data, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Start date must be before end date.' in resp.data

def test_optimize_invalid_num_portfolios(client):
    data = {
        'symbols': 'AAA',
        'start_date': '2024-01-01',
        'end_date': '2024-04-01',
        'num_portfolios': '5',
        'risk_free_rate': '0.0',
    }
    resp = client.post('/optimize', data=data, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Number of portfolios must be an integer between 100 and 10,000.' in resp.data

def test_optimize_invalid_risk_free_rate(client):
    data = {
        'symbols': 'AAA',
        'start_date': '2024-01-01',
        'end_date': '2024-04-01',
        'num_portfolios': '5000',
        'risk_free_rate': 'notanumber',
    }
    resp = client.post('/optimize', data=data, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Risk-free rate must be a valid number.' in resp.data

def test_session_storage(client, monkeypatch):
    # Patch DataLoader and PortfolioOptimizer to skip real computation
    class DummyDL:
        def __init__(self, **kwargs): pass
        def load(self, symbols): pass
        def clean(self): pass
        def filter_dates(self): pass
        def get_data(self): return {'dummy': [1,2,3]}
    class DummyPO:
        def __init__(self, *a, **k): pass
        def run_simulation(self): pass
        def get_metrics_df(self):
            import pandas as pd
            return pd.DataFrame({'Return':[0.1], 'Risk':[0.2], 'Sharpe':[1.5], 'AAA':[1.0]})
        def get_optimal_portfolios(self):
            return {'max_sharpe': {'Risk':0.2, 'Return':0.1, 'AAA':1.0}, 'min_variance': {'Risk':0.2, 'Return':0.1, 'AAA':1.0}, 'max_return': {'Risk':0.2, 'Return':0.1, 'AAA':1.0}}
    monkeypatch.setattr('app.data_loader.DataLoader', DummyDL)
    monkeypatch.setattr('app.portfolio_optimizer.PortfolioOptimizer', DummyPO)
    data = {
        'symbols': 'AAA',
        'start_date': '2024-01-01',
        'end_date': '2024-04-01',
        'num_portfolios': '5000',
        'risk_free_rate': '0.0',
    }
    with client.session_transaction() as sess:
        sess.clear()
    resp = client.post('/optimize', data=data)
    # Should return HTML file
    assert resp.status_code == 200
    assert b'Portfolio Optimization Results' in resp.data
    # Session should store last_metrics_csv and last_inputs
    with client.session_transaction() as sess:
        assert 'last_metrics_csv' in sess
        assert 'last_inputs' in sess
