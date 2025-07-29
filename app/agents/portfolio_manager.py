"""
Portfolio Manager Agent - Specialized agent for portfolio optimization, asset allocation, and investment strategies.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class PortfolioManagerAgent:
    """
    Specialized agent for portfolio management, asset allocation, and investment strategy optimization.
    """
    
    def __init__(self, llm: ChatOpenAI):
        """Initialize the Portfolio Manager Agent."""
        self.llm = llm
        
        self.portfolio_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior portfolio manager with expertise in:
            - Modern Portfolio Theory and asset allocation
            - Risk-return optimization
            - Diversification strategies
            - Investment strategy development
            - Rebalancing and portfolio maintenance
            
            When providing portfolio advice:
            1. Consider risk tolerance and investment timeline
            2. Recommend appropriate asset allocation
            3. Suggest specific asset classes and weightings
            4. Address diversification and correlation
            5. Provide rebalancing guidance
            6. Include cost and tax considerations
            
            Always tailor recommendations to the user's profile and goals."""),
            ("human", "{query}")
        ])
        
        logger.info("Portfolio Manager Agent initialized")
    
    def analyze(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze portfolio requirements and provide recommendations."""
        try:
            # Extract portfolio context from query and user context
            portfolio_context = self._extract_portfolio_context(query, context)
            
            # Generate portfolio recommendations
            recommendations = self._generate_portfolio_recommendations(query, portfolio_context)
            
            return {
                "analysis": recommendations,
                "portfolio_context": portfolio_context,
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat(),
                "asset_allocation": self._extract_asset_allocation(recommendations),
                "risk_level": portfolio_context.get("risk_tolerance", "moderate")
            }
            
        except Exception as e:
            logger.error(f"Error in portfolio analysis: {e}")
            return {
                "analysis": f"Unable to complete portfolio analysis: {str(e)}",
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _extract_portfolio_context(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Extract portfolio-relevant context from query and user context."""
        portfolio_context = {
            "amount": None,
            "risk_tolerance": "moderate",
            "time_horizon": "medium",
            "goals": [],
            "current_portfolio": None
        }
        
        query_lower = query.lower()
        
        # Extract investment amount
        import re
        amount_patterns = [
            r'\$([0-9,]+(?:\.[0-9]{2})?)',
            r'([0-9,]+(?:\.[0-9]{2})?) dollars',
            r'([0-9]+)k',
            r'([0-9]+) thousand'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                amount_str = matches[0].replace(',', '')
                try:
                    if 'k' in query_lower or 'thousand' in query_lower:
                        portfolio_context["amount"] = float(amount_str) * 1000
                    else:
                        portfolio_context["amount"] = float(amount_str)
                    break
                except:
                    pass
        
        # Extract risk tolerance
        if any(word in query_lower for word in ['conservative', 'low risk', 'safe']):
            portfolio_context["risk_tolerance"] = "conservative"
        elif any(word in query_lower for word in ['aggressive', 'high risk', 'growth']):
            portfolio_context["risk_tolerance"] = "aggressive"
        elif any(word in query_lower for word in ['moderate', 'balanced', 'medium']):
            portfolio_context["risk_tolerance"] = "moderate"
        
        # Extract time horizon
        if any(word in query_lower for word in ['short term', 'short-term', '1 year', 'quick']):
            portfolio_context["time_horizon"] = "short"
        elif any(word in query_lower for word in ['long term', 'long-term', 'retirement', '10 year', '20 year']):
            portfolio_context["time_horizon"] = "long"
        
        # Extract goals
        goal_keywords = {
            'retirement': 'retirement planning',
            'house': 'home purchase',
            'education': 'education funding',
            'income': 'income generation',
            'growth': 'capital growth'
        }
        
        for keyword, goal in goal_keywords.items():
            if keyword in query_lower:
                portfolio_context["goals"].append(goal)
        
        # Merge with user context if provided
        if context:
            portfolio_context.update(context)
        
        return portfolio_context
    
    def _generate_portfolio_recommendations(self, query: str, portfolio_context: Dict[str, Any]) -> str:
        """Generate portfolio recommendations based on context."""
        try:
            context_summary = self._format_portfolio_context(portfolio_context)
            
            formatted_prompt = self.portfolio_prompt.format_messages(
                query=f"""Portfolio Analysis Request: {query}

Portfolio Context:
{context_summary}

Please provide:
1. Recommended asset allocation with specific percentages
2. Suggested asset classes and investment vehicles
3. Risk management considerations
4. Implementation strategy
5. Rebalancing recommendations
6. Expected returns and risks"""
            )
            
            response = self.llm.invoke(formatted_prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating portfolio recommendations: {e}")
            return f"Unable to generate portfolio recommendations: {str(e)}"
    
    def _format_portfolio_context(self, context: Dict[str, Any]) -> str:
        """Format portfolio context for prompt."""
        formatted = []
        
        if context.get("amount"):
            formatted.append(f"Investment Amount: ${context['amount']:,.2f}")
        
        formatted.append(f"Risk Tolerance: {context['risk_tolerance']}")
        formatted.append(f"Time Horizon: {context['time_horizon']}")
        
        if context.get("goals"):
            formatted.append(f"Investment Goals: {', '.join(context['goals'])}")
        
        if context.get("current_portfolio"):
            formatted.append(f"Current Portfolio: {context['current_portfolio']}")
        
        return "\n".join(formatted)
    
    def _extract_asset_allocation(self, recommendations: str) -> Dict[str, float]:
        """Extract asset allocation percentages from recommendations."""
        import re
        
        allocation = {}
        
        # Look for percentage patterns
        percentage_patterns = [
            r'(\w+(?:\s+\w+)*)\s*:?\s*([0-9]+)%',
            r'([0-9]+)%\s+(\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*)\s+([0-9]+)\s*percent'
        ]
        
        for pattern in percentage_patterns:
            matches = re.findall(pattern, recommendations, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    asset_class = match[0].strip().lower()
                    try:
                        percentage = float(match[1])
                        if 0 <= percentage <= 100:
                            allocation[asset_class] = percentage
                    except:
                        pass
        
        return allocation