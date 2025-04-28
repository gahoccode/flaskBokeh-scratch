"""
Unit tests for PortfolioOptimizer
"""

import unittest
import numpy as np
import pandas as pd
from app.portfolio_optimizer import PortfolioOptimizer, PortfolioOptimizerError

class TestPortfolioOptimizer(unittest.TestCase):
    def setUp(self):
        # Create dummy price data
        dates = pd.date_range('2024-01-01', periods=10)
        prices = pd.DataFrame({
            'AAA': np.linspace(100, 110, 10),
            'BBB': np.linspace(200, 220, 10),
        }, index=dates)
        self.price_data = prices

    def test_run_simulation_and_metrics(self):
        po = PortfolioOptimizer(self.price_data, num_portfolios=100)
        po.run_simulation()
        df = po.get_metrics_df()
        self.assertEqual(df.shape[0], 100)
        self.assertIn('Return', df.columns)
        self.assertIn('Risk', df.columns)
        self.assertIn('Sharpe', df.columns)
        self.assertIn('AAA', df.columns)
        self.assertIn('BBB', df.columns)

    def test_optimal_portfolios(self):
        po = PortfolioOptimizer(self.price_data, num_portfolios=50)
        po.run_simulation()
        optimal = po.get_optimal_portfolios()
        self.assertIn('max_sharpe', optimal)
        self.assertIn('min_variance', optimal)
        self.assertIn('max_return', optimal)

    def test_error_on_no_data(self):
        po = PortfolioOptimizer(pd.DataFrame(), num_portfolios=10)
        with self.assertRaises(PortfolioOptimizerError):
            po.run_simulation()

if __name__ == '__main__':
    unittest.main()
