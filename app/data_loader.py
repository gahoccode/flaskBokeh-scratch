"""
data_loader.py
Module for loading, cleaning, and filtering financial data for portfolio optimization.
Integrates vnstock and supports loading from GitHub CSV, with robust error handling.
"""

import pandas as pd
import numpy as np
import logging
from rich import print
from vnstock import *  # For future API integration

class DataLoaderError(Exception):
    """Custom exception for DataLoader errors."""
    pass

class DataLoader:
    """
    Loads and processes financial data for portfolio optimization.

    Args:
        source_url (str): URL to CSV data (e.g., GitHub).
        start_date (str): Start date for filtering (YYYY-MM-DD).
        end_date (str): End date for filtering (YYYY-MM-DD).
    """

    def __init__(self, source_url: str, start_date: str = None, end_date: str = None):
        self.source_url = source_url
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.logger = logging.getLogger("DataLoader")
        self.logger.setLevel(logging.INFO)

    def load(self, symbols, interval='1D'):
        """
        Fetch historical close price data for given symbols using vnstock.

        Args:
            symbols (list): List of stock symbols
            interval (str): Data interval (default '1D')

        Returns:
            pd.DataFrame: Cleaned price data indexed by date

        Raises:
            DataLoaderError: If input validation fails or data loading fails
        """
        from vnstock import Quote
        import pandas as pd

        if not isinstance(symbols, list) or not symbols:
            self.logger.error("Symbols must be a non-empty list.")
            raise DataLoaderError("Symbols must be a non-empty list.")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            self.logger.error("Start date must be before end date.")
            raise DataLoaderError("Start date must be before end date.")

        self.logger.info(f"Fetching historical price data for: {symbols}")
        all_historical_data = {}
        for symbol in symbols:
            try:
                self.logger.info(f"Processing {symbol}...")
                quote = Quote(symbol=symbol)
                historical_data = quote.history(
                    start=self.start_date,
                    end=self.end_date,
                    interval=interval,
                    to_df=True
                )
                if not historical_data.empty:
                    all_historical_data[symbol] = historical_data
                    self.logger.info(f"Fetched {len(historical_data)} records for {symbol}")
                else:
                    self.logger.warning(f"No historical data for {symbol}")
            except Exception as e:
                self.logger.error(f"Error fetching data for {symbol}: {e}")
                raise DataLoaderError(f"Error fetching data for {symbol}: {e}")
        # Combine close prices into one DataFrame
        combined_prices = pd.DataFrame()
        for symbol, data in all_historical_data.items():
            try:
                temp_df = data[['time', 'close']].copy()
                temp_df.rename(columns={'close': symbol}, inplace=True)
                if combined_prices.empty:
                    combined_prices = temp_df
                else:
                    combined_prices = pd.merge(combined_prices, temp_df, on='time', how='outer')
            except Exception as e:
                self.logger.error(f"Error combining data for {symbol}: {e}")
                raise DataLoaderError(f"Error combining data for {symbol}: {e}")
        if not combined_prices.empty:
            try:
                combined_prices.rename(columns={'time': 'Date'}, inplace=True)
                combined_prices.set_index(['Date'], inplace=True)
                combined_prices = combined_prices.apply(pd.to_numeric, errors='coerce')
                combined_prices = combined_prices.dropna()
                self.data = combined_prices
                return self.data
            except Exception as e:
                self.logger.error(f"Error cleaning combined price data: {e}")
                raise DataLoaderError(f"Error cleaning combined price data: {e}")
        self.logger.warning("No combined price data available.")
        raise DataLoaderError("No combined price data available.")

    def clean(self):
        """
        Clean and format the loaded price data.
        Ensures all columns are numeric, drops NaNs, and sets index to Date.
        Returns:
            pd.DataFrame: Cleaned DataFrame or None
        """
        if self.data is None:
            self.logger.warning("No data to clean.")
            return None
        df = self.data.copy()
        try:
            df = df.apply(pd.to_numeric, errors="coerce")
            df = df.dropna()
            if 'Date' in df.columns:
                df.set_index('Date', inplace=True)
            self.data = df
            self.logger.info("Data cleaned and formatted.")
            return self.data
        except Exception as e:
            self.logger.error(f"Error during cleaning: {e}")
            return None

    def filter_dates(self):
        """
        Filter data by start_date and end_date.
        Updates self.data in place.
        Returns:
            pd.DataFrame: Filtered DataFrame or None
        """
        if self.data is None:
            self.logger.warning("No data to filter.")
            return None
        df = self.data.copy()
        try:
            if self.start_date:
                df = df[df.index >= self.start_date]
            if self.end_date:
                df = df[df.index <= self.end_date]
            self.data = df
            self.logger.info(f"Data filtered by date: {self.start_date} to {self.end_date}")
            return self.data
        except Exception as e:
            self.logger.error(f"Error during date filtering: {e}")
            return None

    def get_data(self) -> pd.DataFrame:
        """
        Returns the cleaned and filtered price data as a DataFrame, ready for optimization.
        Output DataFrame:
            - Index: Date (str or datetime)
            - Columns: Stock symbols (str), numeric close prices
        Returns:
            pd.DataFrame: Ready-to-use price data
        Raises:
            DataLoaderError: If no data is available or data is invalid
        Example:
            >>> dl = DataLoader(source_url=None, start_date='2024-01-01', end_date='2024-04-01')
            >>> dl.load(['AAA', 'BBB'])
            >>> dl.clean()
            >>> dl.filter_dates()
            >>> df = dl.get_data()
        """
        if self.data is None or not isinstance(self.data, pd.DataFrame) or self.data.empty:
            self.logger.error("No valid data available for optimization.")
            raise DataLoaderError("No valid data available for optimization.")
        return self.data
