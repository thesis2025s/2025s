"""
Market Analyst Agent - Specialized agent for stock analysis, market trends, and sector performance.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage

from app.tools.financial_data import (
    stock_price_tool, 
    company_info_tool, 
    market_overview_tool,
    sector_performance_tool,
    economic_indicators_tool
)

logger = logging.getLogger(__name__)


class MarketAnalystAgent:
    """
    Specialized agent for market analysis, stock research, and sector performance analysis.
    Provides expert-level insights on market trends, company fundamentals, and investment opportunities.
    """
    
    def __init__(self, llm: ChatOpenAI):
        """Initialize the Market Analyst Agent."""
        self.llm = llm
        self.tools = [
            stock_price_tool,
            company_info_tool,
            market_overview_tool,
            sector_performance_tool,
            economic_indicators_tool
        ]
        
        # Specialized prompts for market analysis
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior market analyst with 20+ years of experience in equity research and market analysis. 
            
Your expertise includes:
- Fundamental analysis and company valuation
- Technical analysis and chart patterns
- Sector and industry analysis
- Market trend identification
- Economic indicator interpretation
- Risk assessment for individual stocks and sectors

When analyzing stocks or markets, provide:
1. Current market position and recent performance
2. Key fundamental metrics and their implications
3. Technical indicators and trend analysis
4. Sector comparison and relative strength
5. Key risks and opportunities
6. Investment recommendation with rationale

Use the available tools to gather current data before providing analysis.
Always include confidence levels and cite data sources.
Maintain a professional, analytical tone while making insights accessible."""),
            ("human", "{query}")
        ])
        
        self.sector_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are analyzing sector performance and market trends. Focus on:
            
1. Relative sector performance and rotation patterns
2. Economic drivers affecting each sector
3. Leading and lagging indicators
4. Sector-specific risks and opportunities
5. Correlation with economic cycles
6. Investment themes and trends

Provide actionable insights for sector allocation and stock selection within sectors."""),
            ("human", "{query}")
        ])
        
        self.company_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are conducting detailed company analysis. Examine:
            
1. Business model and competitive position
2. Financial health and profitability trends
3. Growth prospects and market opportunities
4. Management quality and corporate governance
5. Valuation metrics vs. peers and historical levels
6. Key risks and mitigation strategies

Provide a comprehensive investment thesis with clear buy/hold/sell recommendation."""),
            ("human", "{query}")
        ])
        
        logger.info("Market Analyst Agent initialized")
    
    def analyze(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive market analysis based on the query.
        
        Args:
            query: The analysis request (stock, sector, or market analysis)
            context: Additional context about the user's investment profile
            
        Returns:
            Dictionary containing the analysis results and metadata
        """
        try:
            # Determine analysis type
            analysis_type = self._classify_analysis_type(query)
            
            # Gather relevant data
            data_context = self._gather_market_data(query, analysis_type)
            
            # Perform the analysis
            if analysis_type == "company":
                analysis = self._analyze_company(query, data_context, context)
            elif analysis_type == "sector":
                analysis = self._analyze_sector(query, data_context, context)
            elif analysis_type == "market":
                analysis = self._analyze_market(query, data_context, context)
            else:
                analysis = self._general_market_analysis(query, data_context, context)
            
            return {
                "analysis": analysis,
                "analysis_type": analysis_type,
                "data_sources": data_context.get("sources", []),
                "confidence": self._calculate_confidence(data_context),
                "timestamp": datetime.now().isoformat(),
                "recommendations": self._extract_recommendations(analysis),
                "key_metrics": data_context.get("metrics", {}),
                "risks": self._extract_risks(analysis)
            }
            
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return {
                "analysis": f"Unable to complete market analysis: {str(e)}",
                "analysis_type": "error",
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _classify_analysis_type(self, query: str) -> str:
        """Classify the type of market analysis needed."""
        query_lower = query.lower()
        
        # Check for specific stock symbols (basic pattern matching)
        stock_indicators = ["stock", "share", "ticker", "$", "equity"]
        sector_indicators = ["sector", "industry", "etf", "group"]
        market_indicators = ["market", "index", "s&p", "nasdaq", "dow", "overall"]
        
        if any(indicator in query_lower for indicator in stock_indicators):
            # Look for actual stock symbols (3-5 uppercase letters)
            words = query.split()
            for word in words:
                if len(word) >= 2 and len(word) <= 5 and word.isupper():
                    return "company"
            return "company"  # Default to company if stock-related
        
        elif any(indicator in query_lower for indicator in sector_indicators):
            return "sector"
        
        elif any(indicator in query_lower for indicator in market_indicators):
            return "market"
        
        else:
            return "general"
    
    def _gather_market_data(self, query: str, analysis_type: str) -> Dict[str, Any]:
        """Gather relevant market data based on the analysis type."""
        data_context = {"sources": [], "metrics": {}}
        
        try:
            if analysis_type == "company":
                # Extract potential stock symbol from query
                symbol = self._extract_stock_symbol(query)
                if symbol:
                    # Get stock price data
                    price_data = stock_price_tool._run(symbol)
                    data_context["price_data"] = price_data
                    data_context["sources"].append("Stock Price Data")
                    
                    # Get company information
                    company_data = company_info_tool._run(symbol)
                    data_context["company_data"] = company_data
                    data_context["sources"].append("Company Information")
                    
                    # Extract key metrics for confidence calculation
                    data_context["metrics"]["symbol"] = symbol
            
            elif analysis_type == "sector":
                # Get sector performance data
                sector_data = sector_performance_tool._run()
                data_context["sector_data"] = sector_data
                data_context["sources"].append("Sector Performance")
            
            elif analysis_type == "market":
                # Get market overview
                market_data = market_overview_tool._run()
                data_context["market_data"] = market_data
                data_context["sources"].append("Market Overview")
                
                # Get economic indicators
                economic_data = economic_indicators_tool._run()
                data_context["economic_data"] = economic_data
                data_context["sources"].append("Economic Indicators")
            
            # Always get general market context
            if analysis_type != "market":
                try:
                    market_overview = market_overview_tool._run()
                    data_context["market_context"] = market_overview
                    data_context["sources"].append("Market Context")
                except:
                    pass  # Continue without market context if it fails
            
        except Exception as e:
            logger.warning(f"Error gathering market data: {e}")
            data_context["data_error"] = str(e)
        
        return data_context
    
    def _extract_stock_symbol(self, query: str) -> Optional[str]:
        """Extract stock symbol from query."""
        import re
        
        # Look for stock symbols (2-5 uppercase letters, possibly with $)
        patterns = [
            r'\$([A-Z]{1,5})\b',  # $AAPL format
            r'\b([A-Z]{2,5})\b',   # AAPL format
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query)
            if matches:
                return matches[0]
        
        # Common stock names to symbols mapping
        stock_mapping = {
            "apple": "AAPL",
            "microsoft": "MSFT",
            "google": "GOOGL",
            "alphabet": "GOOGL",
            "amazon": "AMZN",
            "tesla": "TSLA",
            "nvidia": "NVDA",
            "meta": "META",
            "facebook": "META",
            "netflix": "NFLX",
            "disney": "DIS",
            "boeing": "BA",
            "coca cola": "KO",
            "walmart": "WMT",
            "visa": "V",
            "mastercard": "MA",
            "jpmorgan": "JPM",
            "berkshire": "BRK.B"
        }
        
        query_lower = query.lower()
        for name, symbol in stock_mapping.items():
            if name in query_lower:
                return symbol
        
        return None
    
    def _analyze_company(self, query: str, data_context: Dict[str, Any], user_context: Optional[Dict] = None) -> str:
        """Perform detailed company analysis."""
        try:
            analysis_input = {
                "query": query,
                "price_data": data_context.get("price_data", "No price data available"),
                "company_data": data_context.get("company_data", "No company data available"),
                "market_context": data_context.get("market_context", "No market context available"),
                "user_context": user_context or {}
            }
            
            formatted_prompt = self.company_analysis_prompt.format_messages(
                query=f"""Analyze this company based on the following data:

Query: {query}

Price Data:
{analysis_input['price_data']}

Company Information:
{analysis_input['company_data']}

Market Context:
{analysis_input['market_context']}

User Context: {analysis_input['user_context']}

Provide a comprehensive analysis with investment recommendation."""
            )
            
            response = self.llm.invoke(formatted_prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"Error in company analysis: {e}")
            return f"Unable to complete company analysis: {str(e)}"
    
    def _analyze_sector(self, query: str, data_context: Dict[str, Any], user_context: Optional[Dict] = None) -> str:
        """Perform sector analysis."""
        try:
            analysis_input = {
                "query": query,
                "sector_data": data_context.get("sector_data", "No sector data available"),
                "market_context": data_context.get("market_context", "No market context available"),
                "user_context": user_context or {}
            }
            
            formatted_prompt = self.sector_analysis_prompt.format_messages(
                query=f"""Analyze sector performance based on the following data:

Query: {query}

Sector Performance Data:
{analysis_input['sector_data']}

Market Context:
{analysis_input['market_context']}

User Context: {analysis_input['user_context']}

Provide sector analysis with investment opportunities and risks."""
            )
            
            response = self.llm.invoke(formatted_prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"Error in sector analysis: {e}")
            return f"Unable to complete sector analysis: {str(e)}"
    
    def _analyze_market(self, query: str, data_context: Dict[str, Any], user_context: Optional[Dict] = None) -> str:
        """Perform overall market analysis."""
        try:
            analysis_input = {
                "query": query,
                "market_data": data_context.get("market_data", "No market data available"),
                "economic_data": data_context.get("economic_data", "No economic data available"),
                "user_context": user_context or {}
            }
            
            formatted_prompt = self.analysis_prompt.format_messages(
                query=f"""Analyze the overall market based on the following data:

Query: {query}

Market Overview:
{analysis_input['market_data']}

Economic Indicators:
{analysis_input['economic_data']}

User Context: {analysis_input['user_context']}

Provide comprehensive market analysis with outlook and investment implications."""
            )
            
            response = self.llm.invoke(formatted_prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return f"Unable to complete market analysis: {str(e)}"
    
    def _general_market_analysis(self, query: str, data_context: Dict[str, Any], user_context: Optional[Dict] = None) -> str:
        """Perform general market analysis for non-specific queries."""
        try:
            formatted_prompt = self.analysis_prompt.format_messages(query=query)
            response = self.llm.invoke(formatted_prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"Error in general analysis: {e}")
            return f"Unable to complete analysis: {str(e)}"
    
    def _calculate_confidence(self, data_context: Dict[str, Any]) -> float:
        """Calculate confidence score based on available data."""
        base_confidence = 0.5
        
        # Increase confidence based on available data sources
        if data_context.get("sources"):
            base_confidence += 0.1 * len(data_context["sources"])
        
        # Increase confidence if we have specific metrics
        if data_context.get("metrics"):
            base_confidence += 0.1
        
        # Decrease confidence if there were data errors
        if data_context.get("data_error"):
            base_confidence -= 0.2
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract key recommendations from the analysis."""
        # Simple extraction based on common recommendation patterns
        recommendations = []
        
        lines = analysis.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'consider']):
                if len(line) > 20 and len(line) < 200:  # Reasonable length
                    recommendations.append(line)
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _extract_risks(self, analysis: str) -> List[str]:
        """Extract key risks from the analysis."""
        risks = []
        
        lines = analysis.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['risk', 'concern', 'challenge', 'threat', 'warning']):
                if len(line) > 20 and len(line) < 200:  # Reasonable length
                    risks.append(line)
        
        return risks[:5]  # Limit to 5 risks
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get a quick market summary."""
        try:
            market_data = market_overview_tool._run()
            economic_data = economic_indicators_tool._run()
            sector_data = sector_performance_tool._run()
            
            return {
                "market_overview": market_data,
                "economic_indicators": economic_data,
                "sector_performance": sector_data,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }