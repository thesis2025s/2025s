"""
Financial data tools for retrieving market data, company information, and economic indicators.
Integrates with multiple financial APIs including Alpha Vantage, Yahoo Finance, and more.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import requests
from functools import lru_cache
import logging
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger(__name__)


class StockPriceInput(BaseModel):
    """Input schema for stock price tool."""
    symbol: str = Field(description="Stock symbol (e.g., AAPL, MSFT)")
    period: str = Field(default="1y", description="Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")


class CompanyInfoInput(BaseModel):
    """Input schema for company information tool."""
    symbol: str = Field(description="Stock symbol (e.g., AAPL, MSFT)")


class MarketDataInput(BaseModel):
    """Input schema for market data tool."""
    symbols: List[str] = Field(description="List of stock symbols")
    metrics: Optional[List[str]] = Field(default=None, description="Specific metrics to retrieve")


class EconomicDataInput(BaseModel):
    """Input schema for economic data tool."""
    indicator: str = Field(description="Economic indicator (e.g., GDP, inflation, unemployment)")
    period: str = Field(default="1y", description="Time period for data")


class FinancialDataError(Exception):
    """Custom exception for financial data errors."""
    pass


class StockPriceTool(BaseTool):
    """Tool for retrieving stock price data and basic technical indicators."""
    
    name = "get_stock_price"
    description = """
    Get current stock price, historical data, and basic technical indicators for a given stock symbol.
    Returns current price, daily change, volume, and key technical indicators like RSI and moving averages.
    """
    args_schema = StockPriceInput
    
    def _run(self, symbol: str, period: str = "1y") -> str:
        """Get stock price data and technical indicators."""
        try:
            # Fetch stock data using yfinance
            stock = yf.Ticker(symbol.upper())
            hist = stock.history(period=period)
            
            if hist.empty:
                return f"No data found for symbol {symbol}"
            
            # Current price and basic info
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            daily_change = current_price - previous_close
            daily_change_pct = (daily_change / previous_close) * 100
            volume = hist['Volume'].iloc[-1]
            
            # Technical indicators
            sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            
            # RSI calculation
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            # 52-week high/low
            high_52w = hist['High'].max()
            low_52w = hist['Low'].min()
            
            result = {
                "symbol": symbol.upper(),
                "current_price": round(current_price, 2),
                "daily_change": round(daily_change, 2),
                "daily_change_percent": round(daily_change_pct, 2),
                "volume": int(volume),
                "sma_20": round(sma_20, 2) if not pd.isna(sma_20) else None,
                "sma_50": round(sma_50, 2) if not pd.isna(sma_50) else None,
                "rsi": round(rsi, 2) if not pd.isna(rsi) else None,
                "52_week_high": round(high_52w, 2),
                "52_week_low": round(low_52w, 2),
                "data_period": period,
                "last_updated": hist.index[-1].strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return f"""Stock Price Data for {symbol.upper()}:
Current Price: ${result['current_price']}
Daily Change: ${result['daily_change']} ({result['daily_change_percent']}%)
Volume: {result['volume']:,}
20-day SMA: ${result['sma_20']}
50-day SMA: ${result['sma_50']}
RSI (14): {result['rsi']}
52-week Range: ${result['52_week_low']} - ${result['52_week_high']}
Last Updated: {result['last_updated']}"""

        except Exception as e:
            logger.error(f"Error fetching stock price for {symbol}: {e}")
            return f"Error retrieving stock price data for {symbol}: {str(e)}"


class CompanyInfoTool(BaseTool):
    """Tool for retrieving detailed company information."""
    
    name = "get_company_info"
    description = """
    Get comprehensive company information including business description, financial metrics,
    key statistics, and fundamental analysis data.
    """
    args_schema = CompanyInfoInput
    
    def _run(self, symbol: str) -> str:
        """Get detailed company information."""
        try:
            stock = yf.Ticker(symbol.upper())
            info = stock.info
            
            if not info:
                return f"No company information found for symbol {symbol}"
            
            # Extract key information
            company_data = {
                "name": info.get("longName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "business_summary": info.get("longBusinessSummary", "N/A"),
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "debt_to_equity": info.get("debtToEquity"),
                "return_on_equity": info.get("returnOnEquity"),
                "return_on_assets": info.get("returnOnAssets"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "profit_margins": info.get("profitMargins"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "employees": info.get("fullTimeEmployees"),
                "headquarters": f"{info.get('city', '')}, {info.get('state', '')}, {info.get('country', '')}".strip(", "),
                "website": info.get("website", "N/A")
            }
            
            # Format financial metrics
            def format_large_number(num):
                if num is None:
                    return "N/A"
                if num >= 1e12:
                    return f"${num/1e12:.2f}T"
                elif num >= 1e9:
                    return f"${num/1e9:.2f}B"
                elif num >= 1e6:
                    return f"${num/1e6:.2f}M"
                else:
                    return f"${num:,.0f}"
            
            def format_percentage(num):
                if num is None:
                    return "N/A"
                return f"{num*100:.2f}%"
            
            def format_ratio(num):
                if num is None:
                    return "N/A"
                return f"{num:.2f}"
            
            result = f"""Company Information for {symbol.upper()}:

Basic Information:
- Company Name: {company_data['name']}
- Sector: {company_data['sector']}
- Industry: {company_data['industry']}
- Headquarters: {company_data['headquarters']}
- Employees: {company_data['employees']:,} if company_data['employees'] else 'N/A'
- Website: {company_data['website']}

Valuation Metrics:
- Market Cap: {format_large_number(company_data['market_cap'])}
- Enterprise Value: {format_large_number(company_data['enterprise_value'])}
- P/E Ratio (TTM): {format_ratio(company_data['pe_ratio'])}
- Forward P/E: {format_ratio(company_data['forward_pe'])}
- PEG Ratio: {format_ratio(company_data['peg_ratio'])}
- Price-to-Book: {format_ratio(company_data['price_to_book'])}

Financial Health:
- Debt-to-Equity: {format_ratio(company_data['debt_to_equity'])}
- Return on Equity: {format_percentage(company_data['return_on_equity'])}
- Return on Assets: {format_percentage(company_data['return_on_assets'])}
- Profit Margins: {format_percentage(company_data['profit_margins'])}

Growth & Dividends:
- Revenue Growth: {format_percentage(company_data['revenue_growth'])}
- Earnings Growth: {format_percentage(company_data['earnings_growth'])}
- Dividend Yield: {format_percentage(company_data['dividend_yield'])}
- Beta: {format_ratio(company_data['beta'])}

Business Summary:
{company_data['business_summary'][:500]}{'...' if len(company_data['business_summary']) > 500 else ''}"""

            return result

        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {e}")
            return f"Error retrieving company information for {symbol}: {str(e)}"


class MarketOverviewTool(BaseTool):
    """Tool for retrieving market overview and major indices."""
    
    name = "get_market_overview"
    description = """
    Get current market overview including major indices (S&P 500, NASDAQ, Dow Jones),
    market sentiment indicators, and sector performance.
    """
    
    def _run(self) -> str:
        """Get market overview data."""
        try:
            # Major indices
            indices = {
                "S&P 500": "^GSPC",
                "NASDAQ": "^IXIC", 
                "Dow Jones": "^DJI",
                "Russell 2000": "^RUT",
                "VIX": "^VIX"
            }
            
            market_data = {}
            for name, symbol in indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="2d")
                    if not hist.empty:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[-2] if len(hist) > 1 else current
                        change = current - previous
                        change_pct = (change / previous) * 100
                        
                        market_data[name] = {
                            "current": current,
                            "change": change,
                            "change_pct": change_pct
                        }
                except Exception as e:
                    logger.warning(f"Could not fetch data for {name}: {e}")
                    continue
            
            # Format market overview
            result = "Market Overview:\n\n"
            
            for name, data in market_data.items():
                if name == "VIX":
                    result += f"{name}: {data['current']:.2f} "
                else:
                    result += f"{name}: {data['current']:,.2f} "
                
                change_str = f"({data['change']:+.2f}, {data['change_pct']:+.2f}%)"
                result += change_str + "\n"
            
            # Add market sentiment interpretation
            if "VIX" in market_data:
                vix_level = market_data["VIX"]["current"]
                if vix_level < 20:
                    sentiment = "Low (Complacent)"
                elif vix_level < 30:
                    sentiment = "Moderate"
                else:
                    sentiment = "High (Fearful)"
                
                result += f"\nMarket Sentiment (VIX): {sentiment}"
            
            return result

        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return f"Error retrieving market overview: {str(e)}"


class SectorPerformanceTool(BaseTool):
    """Tool for retrieving sector performance data."""
    
    name = "get_sector_performance"
    description = """
    Get performance data for major market sectors using sector ETFs.
    Shows relative strength and performance comparison across sectors.
    """
    
    def _run(self) -> str:
        """Get sector performance data."""
        try:
            # Sector ETFs
            sector_etfs = {
                "Technology": "XLK",
                "Healthcare": "XLV", 
                "Financials": "XLF",
                "Consumer Discretionary": "XLY",
                "Communication": "XLC",
                "Industrials": "XLI",
                "Consumer Staples": "XLP",
                "Energy": "XLE",
                "Utilities": "XLU",
                "Real Estate": "XLRE",
                "Materials": "XLB"
            }
            
            sector_performance = {}
            
            for sector, etf in sector_etfs.items():
                try:
                    ticker = yf.Ticker(etf)
                    hist = ticker.history(period="1mo")
                    
                    if not hist.empty:
                        current = hist['Close'].iloc[-1]
                        month_ago = hist['Close'].iloc[0]
                        monthly_return = ((current - month_ago) / month_ago) * 100
                        
                        sector_performance[sector] = {
                            "etf": etf,
                            "current_price": current,
                            "monthly_return": monthly_return
                        }
                except Exception as e:
                    logger.warning(f"Could not fetch data for {sector} ({etf}): {e}")
                    continue
            
            # Sort sectors by performance
            sorted_sectors = sorted(
                sector_performance.items(),
                key=lambda x: x[1]["monthly_return"],
                reverse=True
            )
            
            result = "Sector Performance (1 Month):\n\n"
            
            for i, (sector, data) in enumerate(sorted_sectors, 1):
                result += f"{i:2d}. {sector:<20} ({data['etf']}): {data['monthly_return']:+6.2f}%\n"
            
            return result

        except Exception as e:
            logger.error(f"Error fetching sector performance: {e}")
            return f"Error retrieving sector performance: {str(e)}"


class EconomicIndicatorsTool(BaseTool):
    """Tool for retrieving key economic indicators."""
    
    name = "get_economic_indicators"
    description = """
    Get key economic indicators including interest rates, inflation data,
    unemployment rates, and GDP growth. Useful for macroeconomic analysis.
    """
    
    def _run(self) -> str:
        """Get economic indicators data."""
        try:
            # Economic indicator proxies using market instruments
            indicators = {
                "10-Year Treasury": "^TNX",
                "2-Year Treasury": "^IRX", 
                "USD Index": "DX-Y.NYB",
                "Gold": "GC=F",
                "Oil (WTI)": "CL=F"
            }
            
            economic_data = {}
            
            for name, symbol in indicators.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="5d")
                    
                    if not hist.empty:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[-2] if len(hist) > 1 else current
                        change = current - previous
                        change_pct = (change / previous) * 100
                        
                        economic_data[name] = {
                            "current": current,
                            "change": change,
                            "change_pct": change_pct
                        }
                except Exception as e:
                    logger.warning(f"Could not fetch data for {name}: {e}")
                    continue
            
            result = "Key Economic Indicators:\n\n"
            
            for name, data in economic_data.items():
                if "Treasury" in name:
                    result += f"{name}: {data['current']:.3f}% "
                elif name == "USD Index":
                    result += f"{name}: {data['current']:.2f} "
                else:
                    result += f"{name}: ${data['current']:.2f} "
                
                change_str = f"({data['change']:+.2f}, {data['change_pct']:+.2f}%)"
                result += change_str + "\n"
            
            # Add economic interpretation
            if "10-Year Treasury" in economic_data and "2-Year Treasury" in economic_data:
                ten_year = economic_data["10-Year Treasury"]["current"]
                two_year = economic_data["2-Year Treasury"]["current"]
                yield_curve = ten_year - two_year
                
                result += f"\nYield Curve (10Y-2Y): {yield_curve:.3f}%"
                if yield_curve < 0:
                    result += " (Inverted - Potential recession signal)"
                elif yield_curve < 0.5:
                    result += " (Flattening)"
                else:
                    result += " (Normal)"
            
            return result

        except Exception as e:
            logger.error(f"Error fetching economic indicators: {e}")
            return f"Error retrieving economic indicators: {str(e)}"


class FinancialCalculatorTool(BaseTool):
    """Tool for financial calculations and metrics."""
    
    name = "financial_calculator"
    description = """
    Perform various financial calculations including compound interest, present value,
    future value, loan payments, and investment return analysis.
    """
    
    def _run(self, calculation_type: str, **kwargs) -> str:
        """Perform financial calculations."""
        try:
            if calculation_type.lower() == "compound_interest":
                principal = kwargs.get("principal", 0)
                rate = kwargs.get("rate", 0) / 100  # Convert percentage to decimal
                time = kwargs.get("time", 0)
                compound_frequency = kwargs.get("compound_frequency", 1)
                
                future_value = principal * (1 + rate/compound_frequency) ** (compound_frequency * time)
                total_interest = future_value - principal
                
                return f"""Compound Interest Calculation:
Principal: ${principal:,.2f}
Annual Interest Rate: {rate*100:.2f}%
Time Period: {time} years
Compounding Frequency: {compound_frequency}x per year

Future Value: ${future_value:,.2f}
Total Interest Earned: ${total_interest:,.2f}
Effective Annual Return: {((future_value/principal)**(1/time) - 1)*100:.2f}%"""

            elif calculation_type.lower() == "present_value":
                future_value = kwargs.get("future_value", 0)
                rate = kwargs.get("rate", 0) / 100
                time = kwargs.get("time", 0)
                
                present_value = future_value / ((1 + rate) ** time)
                
                return f"""Present Value Calculation:
Future Value: ${future_value:,.2f}
Discount Rate: {rate*100:.2f}%
Time Period: {time} years

Present Value: ${present_value:,.2f}
Total Discount: ${future_value - present_value:,.2f}"""

            else:
                return f"Calculation type '{calculation_type}' not supported. Available types: compound_interest, present_value"

        except Exception as e:
            logger.error(f"Error in financial calculation: {e}")
            return f"Error performing financial calculation: {str(e)}"


# Create tool instances
stock_price_tool = StockPriceTool()
company_info_tool = CompanyInfoTool()
market_overview_tool = MarketOverviewTool()
sector_performance_tool = SectorPerformanceTool()
economic_indicators_tool = EconomicIndicatorsTool()
financial_calculator_tool = FinancialCalculatorTool()

# List of all financial tools
FINANCIAL_TOOLS = [
    stock_price_tool,
    company_info_tool,
    market_overview_tool,
    sector_performance_tool,
    economic_indicators_tool,
    financial_calculator_tool
]


def get_financial_tools() -> List[BaseTool]:
    """Get all available financial tools."""
    return FINANCIAL_TOOLS


# Helper functions for external use
@lru_cache(maxsize=100)
def get_stock_quote(symbol: str) -> Dict[str, Any]:
    """Get basic stock quote data with caching."""
    try:
        stock = yf.Ticker(symbol.upper())
        hist = stock.history(period="1d")
        
        if hist.empty:
            return {"error": f"No data found for {symbol}"}
        
        return {
            "symbol": symbol.upper(),
            "price": hist['Close'].iloc[-1],
            "volume": hist['Volume'].iloc[-1],
            "timestamp": hist.index[-1].isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


def validate_symbol(symbol: str) -> bool:
    """Validate if a stock symbol exists."""
    try:
        stock = yf.Ticker(symbol.upper())
        hist = stock.history(period="1d")
        return not hist.empty
    except:
        return False