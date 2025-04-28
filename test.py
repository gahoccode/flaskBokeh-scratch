from vnstock import Quote
import pandas as pd
import numpy as np

def load_stock_data(symbols, start_date, end_date, interval='1D'):
    """
    Load historical stock data using vnstock
    
    Args:
        symbols (list): List of stock symbols
        start_date (str): Start date in format 'YYYY-MM-DD'
        end_date (str): End date in format 'YYYY-MM-DD'
        interval (str): Data interval ('1D' for daily)
    
    Returns:
        DataFrame: Processed data ready for optimization
    """
    print(f"Fetching historical price data for: {symbols}")
    
    # Dictionary to store historical data for each symbol
    all_historical_data = {}
    
    # Fetch historical data for each symbol
    for symbol in symbols:
        try:
            print(f"\nProcessing {symbol}...")
            quote = Quote(symbol=symbol)
            
            # Fetch historical price data
            historical_data = quote.history(
                start=start_date,
                end=end_date,
                interval=interval,
                to_df=True
            )
            
            if not historical_data.empty:
                all_historical_data[symbol] = historical_data
                print(f"Successfully fetched {len(historical_data)} records for {symbol}")
            else:
                print(f"No historical data available for {symbol}")
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    
    # Create a combined DataFrame for close prices
    combined_prices = pd.DataFrame()
    
    for symbol, data in all_historical_data.items():
        if not historical_data.empty:
            # Extract time and close price
            temp_df = data[['time', 'close']].copy()
            temp_df.rename(columns={'close': symbol}, inplace=True)
            
            if combined_prices.empty:
                combined_prices = temp_df
            else:
                combined_prices = pd.merge(combined_prices, temp_df, on='time', how='outer')
    
    # Clean and format data for optimization
    if not combined_prices.empty:
        combined_prices.rename(columns={'time': 'Date'}, inplace=True)
        combined_prices.set_index(['Date'], inplace=True)
        combined_prices = combined_prices.apply(pd.to_numeric, errors='coerce')
        combined_prices = combined_prices.dropna()
        
        return combined_prices
    
    return None