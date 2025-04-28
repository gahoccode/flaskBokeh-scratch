"""
portfolio_optimizer.py
Monte Carlo-based portfolio optimization for financial assets.

Module Purpose:
    - Provides PortfolioOptimizer class for simulating and analyzing random portfolios.
    - Supports calculation of returns, risk (volatility), Sharpe ratio, and optimal portfolios.

Key Classes:
    - PortfolioOptimizer: Main optimizer class
    - PortfolioOptimizerError: Custom exception

Assumptions & Limitations:
    - Input price_data must be a cleaned DataFrame (date index, asset columns, no NaNs)
    - Uses log returns and annualizes with 252 trading days
    - Monte Carlo simulation does not guarantee global optimum; only explores random portfolios
    - Not suitable for highly illiquid or non-numeric data

Example Usage:
    >>> po = PortfolioOptimizer(price_data)
    >>> po.run_simulation()
    >>> metrics = po.get_metrics_df()
    >>> optimal = po.get_optimal_portfolios()

"""

import numpy as np
import pandas as pd
import logging
from rich import print

class PortfolioOptimizerError(Exception):
    """Custom exception for PortfolioOptimizer errors."""
    pass

class PortfolioOptimizer:
    """
    Performs portfolio optimization using Monte Carlo simulation.

    Args:
        price_data (pd.DataFrame): Cleaned price data (Date index, asset columns)
        num_portfolios (int): Number of random portfolios to simulate
        risk_free_rate (float): Risk-free rate for Sharpe ratio calculation

    Example:
        >>> po = PortfolioOptimizer(price_data)
        >>> po.run_simulation()
        >>> df = po.get_metrics_df()
        >>> optimal = po.get_optimal_portfolios()
    """

    def __init__(self, price_data: pd.DataFrame, num_portfolios: int = 5000, risk_free_rate: float = 0.0):
        """
        Initialize PortfolioOptimizer.

        Args:
            price_data (pd.DataFrame): Cleaned price data (date index, asset columns)
            num_portfolios (int): Number of random portfolios to simulate
            risk_free_rate (float): Risk-free rate for Sharpe ratio calculation
        """
        self.price_data = price_data
        self.num_portfolios = num_portfolios
        self.risk_free_rate = risk_free_rate
        self.logger = logging.getLogger("PortfolioOptimizer")
        self.logger.setLevel(logging.INFO)
        self.results = None

    def run_simulation(self):
        """
        Run Monte Carlo simulation to generate random portfolios and calculate returns and risk.
        Populates self.results with all weights, returns, risk, and Sharpe ratios.
        Returns:
            dict: Results containing weights, returns, risk, Sharpe ratios
        Raises:
            PortfolioOptimizerError: If input data is invalid or calculation fails
        """
        try:
            if self.price_data is None or not isinstance(self.price_data, pd.DataFrame) or self.price_data.empty:
                self.logger.error("Invalid or empty price data for optimization.")
                raise PortfolioOptimizerError("Invalid or empty price data for optimization.")
            num_assets = self.price_data.shape[1]
            log_ret = np.log(self.price_data / self.price_data.shift(1))
            cov_matrix = log_ret.cov() * 252
            all_wts = np.zeros((self.num_portfolios, num_assets))
            port_returns = np.zeros(self.num_portfolios)
            port_risk = np.zeros(self.num_portfolios)
            sharpe_ratio = np.zeros(self.num_portfolios)
            np.random.seed(42)
            for i in range(self.num_portfolios):
                wts = np.random.uniform(size=num_assets)
                wts = wts / np.sum(wts)
                all_wts[i, :] = wts
                port_ret = np.sum(log_ret.mean() * wts)
                port_ret = (port_ret + 1) ** 252 - 1
                port_returns[i] = port_ret
                port_sd = np.sqrt(np.dot(wts.T, np.dot(cov_matrix, wts)))
                port_risk[i] = port_sd
                sr = (port_ret - self.risk_free_rate) / port_sd if port_sd > 0 else 0.0
                sharpe_ratio[i] = sr
            self.results = {
                'weights': all_wts,
                'returns': port_returns,
                'risk': port_risk,
                'sharpe_ratio': sharpe_ratio
            }
            self.logger.info(f"Simulation complete: {self.num_portfolios} portfolios simulated.")
            return self.results
        except Exception as e:
            self.logger.error(f"Error during simulation: {e}")
            raise PortfolioOptimizerError(f"Error during simulation: {e}")

    def get_metrics_df(self) -> pd.DataFrame:
        """
        Return a DataFrame of portfolio metrics: returns, risk, Sharpe ratio, and weights.
        Returns:
            pd.DataFrame: Each row is a portfolio; columns are metrics and weights
        Raises:
            PortfolioOptimizerError: If simulation has not been run or fails
        """
        try:
            if self.results is None:
                self.logger.error("Simulation not run. Call run_simulation() first.")
                raise PortfolioOptimizerError("Simulation not run. Call run_simulation() first.")
            num_assets = self.price_data.shape[1]
            columns = ['Return', 'Risk', 'Sharpe'] + list(self.price_data.columns)
            data = np.concatenate([
                self.results['returns'].reshape(-1, 1),
                self.results['risk'].reshape(-1, 1),
                self.results['sharpe_ratio'].reshape(-1, 1),
                self.results['weights']
            ], axis=1)
            df = pd.DataFrame(data, columns=columns)
            return df
        except Exception as e:
            self.logger.error(f"Error in get_metrics_df: {e}")
            raise PortfolioOptimizerError(f"Error in get_metrics_df: {e}")

    def get_optimal_portfolios(self):
        """
        Identify optimal portfolios: max Sharpe ratio, min variance, max return.
        Returns:
            dict: {'max_sharpe': {...}, 'min_variance': {...}, 'max_return': {...}}
        Raises:
            PortfolioOptimizerError: If simulation has not been run or fails
        """
        try:
            df = self.get_metrics_df()
            max_sharpe_idx = df['Sharpe'].idxmax()
            min_var_idx = df['Risk'].idxmin()
            max_ret_idx = df['Return'].idxmax()
            return {
                'max_sharpe': df.loc[max_sharpe_idx].to_dict(),
                'min_variance': df.loc[min_var_idx].to_dict(),
                'max_return': df.loc[max_ret_idx].to_dict()
            }
        except Exception as e:
            self.logger.error(f"Error in get_optimal_portfolios: {e}")
            raise PortfolioOptimizerError(f"Error in get_optimal_portfolios: {e}")

    def get_visualization_data(self):
        """
        Prepare all results for visualization (metrics DataFrame, optimal portfolios, raw arrays).
        Returns:
            dict: {'metrics_df': DataFrame, 'optimal': dict, 'raw': dict}
        Raises:
            PortfolioOptimizerError: If simulation not run or fails
        """
        try:
            metrics_df = self.get_metrics_df()
            optimal = self.get_optimal_portfolios()
            raw = self.results.copy() if self.results else None
            return {
                'metrics_df': metrics_df,
                'optimal': optimal,
                'raw': raw
            }
        except Exception as e:
            self.logger.error(f"Error in get_visualization_data: {e}")
            raise PortfolioOptimizerError(f"Error in get_visualization_data: {e}")
