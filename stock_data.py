"""
Stock data fetching module using yfinance.
Fetches historical stock data for testing.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class StockDataFetcher:
    """Fetches and manages stock price data."""
    
    def __init__(self):
        """Initialize the stock data fetcher."""
        pass
    
    def fetch_stock_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str
    ) -> Optional[pd.DataFrame]:
        """
        Fetch stock data for a given ticker and date range.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            
        Returns:
            DataFrame with stock data or None if fetch fails
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            
            if data.empty:
                print(f"Warning: No data found for {ticker}")
                return None
                
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
    
    def get_price_at_date(
        self,
        ticker: str,
        date: str
    ) -> Optional[float]:
        """
        Get closing price for a stock at a specific date.
        
        Args:
            ticker: Stock ticker symbol
            date: Date in 'YYYY-MM-DD' format
            
        Returns:
            Closing price or None if not available
        """
        # Fetch data for a range around the date to handle weekends/holidays
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        start_date = (date_obj - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = (date_obj + timedelta(days=7)).strftime('%Y-%m-%d')
        
        data = self.fetch_stock_data(ticker, start_date, end_date)
        
        if data is None or data.empty:
            return None
        
        # Find the closest date
        target_date = pd.to_datetime(date)
        data.index = pd.to_datetime(data.index)
        
        # Get the closest date that's not in the future
        valid_dates = data.index[data.index <= target_date]
        if len(valid_dates) == 0:
            return None
            
        closest_date = valid_dates[-1]
        return float(data.loc[closest_date]['Close'])
    
    def get_historical_context(
        self,
        ticker: str,
        cutoff_date: str,
        lookback_days: int = 90
    ) -> Dict[str, Any]:
        """
        Get historical context data up to cutoff date.
        
        Args:
            ticker: Stock ticker symbol
            cutoff_date: Cutoff date in 'YYYY-MM-DD' format
            lookback_days: Number of days to look back
            
        Returns:
            Dictionary with historical context
        """
        cutoff = datetime.strptime(cutoff_date, '%Y-%m-%d')
        start_date = (cutoff - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
        
        data = self.fetch_stock_data(ticker, start_date, cutoff_date)
        
        if data is None or data.empty:
            return {}
        
        context = {
            'ticker': ticker,
            'cutoff_date': cutoff_date,
            'lookback_days': lookback_days,
            'latest_close': float(data['Close'].iloc[-1]),
            'average_close': float(data['Close'].mean()),
            'high': float(data['High'].max()),
            'low': float(data['Low'].min()),
            'volatility': float(data['Close'].std()),
            'price_change_pct': float(
                ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
            ),
        }
        
        return context
