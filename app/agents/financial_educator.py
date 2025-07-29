"""
Financial Educator Agent - Specialized agent for financial education and concept explanation.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class FinancialEducatorAgent:
    """Specialized agent for financial education and concept explanation."""
    
    def __init__(self, llm: ChatOpenAI):
        """Initialize the Financial Educator Agent."""
        self.llm = llm
        
        self.education_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial educator and expert teacher specializing in:
            - Financial concept explanations
            - Investment education
            - Personal finance guidance
            - Market mechanics and terminology
            - Financial planning principles
            
            When educating users:
            1. Use clear, accessible language
            2. Provide practical examples
            3. Break down complex concepts
            4. Include relevant analogies
            5. Offer actionable steps
            6. Encourage further learning
            
            Adapt your explanation level to the user's apparent knowledge level."""),
            ("human", "{query}")
        ])
        
        logger.info("Financial Educator Agent initialized")
    
    def educate(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Provide financial education content."""
        try:
            educational_content = self._generate_educational_content(query, context)
            
            return {
                "content": educational_content,
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat(),
                "learning_level": self._assess_complexity_level(query),
                "related_topics": self._suggest_related_topics(query)
            }
            
        except Exception as e:
            logger.error(f"Error in financial education: {e}")
            return {
                "content": f"Unable to provide educational content: {str(e)}",
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _generate_educational_content(self, query: str, context: Optional[Dict] = None) -> str:
        """Generate educational content based on query."""
        try:
            context_info = ""
            if context:
                knowledge_level = context.get("knowledge_level", "beginner")
                context_info = f"\nUser Knowledge Level: {knowledge_level}"
            
            formatted_prompt = self.education_prompt.format_messages(
                query=f"{query}{context_info}"
            )
            
            response = self.llm.invoke(formatted_prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating educational content: {e}")
            return f"Unable to generate educational content: {str(e)}"
    
    def _assess_complexity_level(self, query: str) -> str:
        """Assess the complexity level of the query."""
        query_lower = query.lower()
        
        advanced_terms = ['derivatives', 'options', 'futures', 'hedge', 'arbitrage', 'volatility']
        basic_terms = ['what is', 'explain', 'how does', 'basic', 'simple']
        
        if any(term in query_lower for term in advanced_terms):
            return "advanced"
        elif any(term in query_lower for term in basic_terms):
            return "beginner"
        else:
            return "intermediate"
    
    def _suggest_related_topics(self, query: str) -> List[str]:
        """Suggest related educational topics."""
        query_lower = query.lower()
        
        topic_map = {
            'stock': ['dividends', 'market cap', 'P/E ratio', 'earnings'],
            'bond': ['yield', 'duration', 'credit rating', 'interest rates'],
            'portfolio': ['diversification', 'asset allocation', 'rebalancing', 'risk tolerance'],
            'retirement': ['401k', 'IRA', 'compound interest', 'withdrawal strategies'],
            'risk': ['volatility', 'beta', 'correlation', 'hedging']
        }
        
        related_topics = []
        for key, topics in topic_map.items():
            if key in query_lower:
                related_topics.extend(topics)
                break
        
        return related_topics[:5]  # Limit to 5 suggestions