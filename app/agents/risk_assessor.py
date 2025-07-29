"""
Risk Assessor Agent - Specialized agent for risk assessment and analysis.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class RiskAssessorAgent:
    """Specialized agent for risk assessment and analysis."""
    
    def __init__(self, llm: ChatOpenAI):
        """Initialize the Risk Assessor Agent."""
        self.llm = llm
        
        self.risk_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a risk management specialist with expertise in:
            - Financial risk assessment
            - Volatility analysis
            - Scenario analysis and stress testing
            - Risk mitigation strategies
            - Regulatory risk considerations
            
            When assessing risks:
            1. Identify all relevant risk types
            2. Quantify risks where possible
            3. Assess probability and impact
            4. Recommend mitigation strategies
            5. Consider correlation and systemic risks
            6. Provide clear risk ratings"""),
            ("human", "{query}")
        ])
        
        logger.info("Risk Assessor Agent initialized")
    
    def analyze(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform risk assessment analysis."""
        try:
            risk_analysis = self._perform_risk_analysis(query, context)
            
            return {
                "analysis": risk_analysis,
                "confidence": 0.75,
                "timestamp": datetime.now().isoformat(),
                "risk_factors": self._extract_risk_factors(risk_analysis),
                "risk_level": self._assess_overall_risk_level(risk_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error in risk analysis: {e}")
            return {
                "analysis": f"Unable to complete risk analysis: {str(e)}",
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _perform_risk_analysis(self, query: str, context: Optional[Dict] = None) -> str:
        """Perform detailed risk analysis."""
        try:
            context_info = ""
            if context:
                context_info = f"\nUser Context: {context}"
            
            formatted_prompt = self.risk_prompt.format_messages(
                query=f"{query}{context_info}"
            )
            
            response = self.llm.invoke(formatted_prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"Error performing risk analysis: {e}")
            return f"Unable to perform risk analysis: {str(e)}"
    
    def _extract_risk_factors(self, analysis: str) -> List[Dict[str, Any]]:
        """Extract risk factors from analysis."""
        # Simple extraction logic
        risk_factors = []
        lines = analysis.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['risk', 'volatility', 'uncertainty', 'threat']):
                if len(line) > 20:
                    risk_factors.append({
                        "description": line,
                        "type": "general",
                        "severity": "medium"  # Default severity
                    })
        
        return risk_factors[:10]  # Limit to 10 risk factors
    
    def _assess_overall_risk_level(self, analysis: str) -> str:
        """Assess overall risk level from analysis."""
        analysis_lower = analysis.lower()
        
        high_risk_indicators = ['high risk', 'significant risk', 'volatile', 'dangerous', 'avoid']
        low_risk_indicators = ['low risk', 'safe', 'stable', 'conservative', 'minimal risk']
        
        high_count = sum(1 for indicator in high_risk_indicators if indicator in analysis_lower)
        low_count = sum(1 for indicator in low_risk_indicators if indicator in analysis_lower)
        
        if high_count > low_count:
            return "high"
        elif low_count > high_count:
            return "low"
        else:
            return "moderate"