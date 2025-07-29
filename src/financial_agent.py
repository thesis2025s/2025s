"""
Core Financial AI Agent
Provides intelligent financial analysis and Q&A capabilities
"""
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain.agents import Tool, AgentExecutor, initialize_agent, AgentType
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from config import settings
from src.data_sources import financial_data
from src.knowledge_base import FinancialKnowledgeBase

logger = logging.getLogger(__name__)

class StockAnalysisTool(BaseTool):
    """Tool for analyzing stocks and providing investment insights"""
    
    name = "stock_analysis"
    description = "Analyze stocks, get current prices, financial metrics, and investment insights for any stock symbol"
    
    def _run(self, symbol: str) -> str:
        """Run stock analysis for given symbol"""
        try:
            # Get stock data
            stock_data = financial_data.get_stock_data(symbol, "1y")
            company_info = financial_data.get_company_info(symbol)
            technical_indicators = financial_data.calculate_technical_indicators(symbol)
            
            if stock_data.empty:
                return f"Could not retrieve data for symbol {symbol}. Please check if the symbol is valid."
            
            # Calculate performance metrics
            current_price = stock_data['Close'].iloc[-1]
            year_start = stock_data['Close'].iloc[0]
            ytd_performance = ((current_price / year_start) - 1) * 100
            
            # Build analysis response
            analysis = f"""
            **Stock Analysis for {symbol}**
            
            **Company Information:**
            - Name: {company_info.get('name', 'N/A')}
            - Sector: {company_info.get('sector', 'N/A')}
            - Industry: {company_info.get('industry', 'N/A')}
            
            **Current Metrics:**
            - Current Price: ${technical_indicators.get('current_price', 'N/A')}
            - Year-to-Date Performance: {ytd_performance:.2f}%
            - Market Cap: ${company_info.get('marketCap', 0):,}
            - P/E Ratio: {company_info.get('peRatio', 'N/A')}
            - Beta: {company_info.get('beta', 'N/A')}
            
            **Technical Indicators:**
            - 20-day SMA: ${technical_indicators.get('sma_20', 'N/A')}
            - 50-day SMA: ${technical_indicators.get('sma_50', 'N/A')}
            - RSI: {technical_indicators.get('rsi', 'N/A')}
            - 52-week High: ${technical_indicators.get('high_52w', 'N/A')}
            - 52-week Low: ${technical_indicators.get('low_52w', 'N/A')}
            """
            
            return analysis.strip()
            
        except Exception as e:
            logger.error(f"Error in stock analysis for {symbol}: {e}")
            return f"Error analyzing stock {symbol}: {str(e)}"

class MarketOverviewTool(BaseTool):
    """Tool for providing market overview and sector analysis"""
    
    name = "market_overview"
    description = "Get market overview, sector performance, and general market conditions"
    
    def _run(self, query: str = "") -> str:
        """Run market overview analysis"""
        try:
            sector_performance = financial_data.get_sector_performance()
            
            # Get major indices
            indices = ['SPY', 'QQQ', 'DIA', 'IWM']  # S&P 500, NASDAQ, Dow, Russell 2000
            index_data = {}
            
            for index in indices:
                data = financial_data.get_stock_data(index, "1mo")
                if not data.empty:
                    current = data['Close'].iloc[-1]
                    month_start = data['Close'].iloc[0]
                    performance = ((current / month_start) - 1) * 100
                    index_data[index] = {
                        'price': round(current, 2),
                        'performance_1m': round(performance, 2)
                    }
            
            overview = f"""
            **Market Overview**
            
            **Major Indices (1-Month Performance):**
            """
            
            for symbol, data in index_data.items():
                overview += f"\n- {symbol}: ${data['price']} ({data['performance_1m']:+.2f}%)"
            
            overview += "\n\n**Sector Performance (1-Month):**"
            for sector, data in sector_performance.items():
                overview += f"\n- {sector}: {data['performance_1m']:+.2f}%"
            
            return overview.strip()
            
        except Exception as e:
            logger.error(f"Error in market overview: {e}")
            return f"Error generating market overview: {str(e)}"

class EconomicDataTool(BaseTool):
    """Tool for economic data and indicators"""
    
    name = "economic_data"
    description = "Get economic indicators, inflation data, GDP, unemployment, and other macroeconomic data"
    
    def _run(self, indicator: str) -> str:
        """Get economic data for specified indicator"""
        try:
            # For demo purposes, we'll provide general economic insights
            # In production, this would connect to FRED API or similar
            
            economic_info = {
                'inflation': "Current inflation trends and Federal Reserve policy impacts",
                'gdp': "GDP growth rates and economic expansion indicators",
                'unemployment': "Employment statistics and labor market conditions",
                'interest_rates': "Federal funds rate and yield curve analysis"
            }
            
            if indicator.lower() in economic_info:
                return f"Economic Data - {indicator.title()}: {economic_info[indicator.lower()]}"
            else:
                return "Available economic indicators: inflation, GDP, unemployment, interest_rates"
                
        except Exception as e:
            logger.error(f"Error fetching economic data: {e}")
            return f"Error retrieving economic data: {str(e)}"

class FinancialAgent:
    """Main Financial AI Agent"""
    
    def __init__(self):
        """Initialize the financial agent"""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            openai_api_key=settings.openai_api_key
        )
        
        # Initialize knowledge base
        self.knowledge_base = FinancialKnowledgeBase()
        
        # Setup memory
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10  # Keep last 10 exchanges
        )
        
        # Initialize tools
        self.tools = [
            StockAnalysisTool(),
            MarketOverviewTool(),
            EconomicDataTool()
        ]
        
        # Create agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=settings.debug,
            handle_parsing_errors=True
        )
        
        # System prompt for financial expertise
        self.system_prompt = """
        You are an expert financial advisor and analyst with deep knowledge of:
        - Stock market analysis and investment strategies
        - Economic indicators and their market impacts
        - Risk management and portfolio optimization
        - Financial statements and valuation methods
        - Technical analysis and market trends
        
        Provide accurate, data-driven financial advice while being clear about risks and limitations.
        Always cite your sources and explain your reasoning.
        If you're uncertain about something, say so and suggest where to find more information.
        
        When analyzing stocks or making recommendations:
        1. Consider both fundamental and technical factors
        2. Assess risk-reward profiles
        3. Provide context about market conditions
        4. Suggest appropriate time horizons
        5. Mention important risks and limitations
        """
    
    def ask(self, question: str, context: Optional[Dict] = None) -> str:
        """
        Ask the financial agent a question
        
        Args:
            question: The financial question to ask
            context: Optional context for the question
            
        Returns:
            The agent's response
        """
        try:
            # Add context to the question if provided
            if context:
                question = f"Context: {context}\n\nQuestion: {question}"
            
            # Get knowledge base context
            kb_context = self.knowledge_base.search(question)
            if kb_context:
                question = f"Relevant financial knowledge: {kb_context}\n\n{question}"
            
            # Query the agent
            response = self.agent.run(input=question)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return f"I apologize, but I encountered an error processing your question: {str(e)}"
    
    def get_financial_summary(self, symbols: List[str]) -> str:
        """
        Get a comprehensive financial summary for multiple symbols
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Comprehensive financial summary
        """
        try:
            summaries = []
            
            for symbol in symbols[:5]:  # Limit to 5 symbols
                analysis = self.tools[0]._run(symbol)  # Use stock analysis tool
                summaries.append(analysis)
            
            # Combine with market overview
            market_overview = self.tools[1]._run("")
            
            full_summary = "**Portfolio Analysis Summary**\n\n"
            full_summary += "\n\n".join(summaries)
            full_summary += f"\n\n{market_overview}"
            
            return full_summary
            
        except Exception as e:
            logger.error(f"Error generating financial summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()

# Global agent instance
financial_agent = FinancialAgent()