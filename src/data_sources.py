"""
Financial Data Sources Integration
Provides unified access to various financial data APIs
"""
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging
from config import settings

logger = logging.getLogger(__name__)

class FinancialDataManager:
    """Manages access to multiple financial data sources"""
    
    def __init__(self):
        self.alpha_vantage_key = settings.alpha_vantage_api_key
        self.alpha_vantage_base = settings.alpha_vantage_base_url
        
    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Get stock data using Yahoo Finance
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            return data
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_company_info(self, symbol: str) -> Dict:
        """
        Get company information
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'marketCap': info.get('marketCap', 0),
                'peRatio': info.get('trailingPE', 0),
                'dividendYield': info.get('dividendYield', 0),
                'beta': info.get('beta', 0),
                'description': info.get('longBusinessSummary', '')
            }
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {e}")
            return {}
    
    def get_financial_statements(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """
        Get financial statements for a company
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with income statement, balance sheet, and cash flow
        """
        try:
            ticker = yf.Ticker(symbol)
            return {
                'income_statement': ticker.financials,
                'balance_sheet': ticker.balance_sheet,
                'cash_flow': ticker.cashflow
            }
        except Exception as e:
            logger.error(f"Error fetching financial statements for {symbol}: {e}")
            return {}
    
    def get_economic_indicator(self, indicator: str) -> Dict:
        """
        Get economic indicators from Alpha Vantage
        
        Args:
            indicator: Economic indicator (e.g., 'REAL_GDP', 'INFLATION', 'UNEMPLOYMENT')
            
        Returns:
            Dictionary with economic data
        """
        if not self.alpha_vantage_key:
            logger.warning("Alpha Vantage API key not configured")
            return {}
            
        try:
            url = f"{self.alpha_vantage_base}/query"
            params = {
                'function': indicator,
                'apikey': self.alpha_vantage_key,
                'datatype': 'json'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching economic indicator {indicator}: {e}")
            return {}
    
    def get_market_news(self, symbol: str = None, limit: int = 10) -> List[Dict]:
        """
        Get market news for a symbol or general market news
        
        Args:
            symbol: Stock symbol (optional)
            limit: Number of news items to return
            
        Returns:
            List of news items
        """
        try:
            if symbol:
                ticker = yf.Ticker(symbol)
                news = ticker.news[:limit]
            else:
                # Get general market news (this is a simplified example)
                # In a real implementation, you'd use a news API
                news = []
            
            return [
                {
                    'title': item.get('title', ''),
                    'summary': item.get('summary', ''),
                    'url': item.get('link', ''),
                    'timestamp': item.get('providerPublishTime', 0)
                }
                for item in news
            ]
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    def get_sector_performance(self) -> Dict:
        """
        Get sector performance data
        
        Returns:
            Dictionary with sector performance data
        """
        try:
            sectors = [
                'XLK',  # Technology
                'XLF',  # Financial
                'XLV',  # Healthcare
                'XLE',  # Energy
                'XLI',  # Industrial
                'XLY',  # Consumer Discretionary
                'XLP',  # Consumer Staples
                'XLRE', # Real Estate
                'XLU',  # Utilities
                'XLB'   # Materials
            ]
            
            sector_data = {}
            for sector in sectors:
                data = self.get_stock_data(sector, "1mo")
                if not data.empty:
                    performance = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
                    sector_data[sector] = {
                        'performance_1m': round(performance, 2),
                        'current_price': round(data['Close'].iloc[-1], 2)
                    }
            
            return sector_data
        except Exception as e:
            logger.error(f"Error fetching sector performance: {e}")
            return {}
    
    def calculate_technical_indicators(self, symbol: str, period: str = "6mo") -> Dict:
        """
        Calculate basic technical indicators
        
        Args:
            symbol: Stock symbol
            period: Time period for calculation
            
        Returns:
            Dictionary with technical indicators
        """
        try:
            data = self.get_stock_data(symbol, period)
            if data.empty:
                return {}
            
            # Simple Moving Averages
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            
            # RSI calculation (simplified)
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_price = data['Close'].iloc[-1]
            
            return {
                'current_price': round(current_price, 2),
                'sma_20': round(data['SMA_20'].iloc[-1], 2) if not pd.isna(data['SMA_20'].iloc[-1]) else None,
                'sma_50': round(data['SMA_50'].iloc[-1], 2) if not pd.isna(data['SMA_50'].iloc[-1]) else None,
                'rsi': round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else None,
                'volume': int(data['Volume'].iloc[-1]),
                'high_52w': round(data['High'].max(), 2),
                'low_52w': round(data['Low'].min(), 2)
            }
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {symbol}: {e}")
            return {}

# Global instance
financial_data = FinancialDataManager()