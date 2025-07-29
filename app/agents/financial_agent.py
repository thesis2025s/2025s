"""
Financial Specialist AI Agent - Main orchestration using LangGraph.
This module contains the primary agent that coordinates multiple specialized financial agents.
"""

import json
import logging
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from datetime import datetime

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.tools import BaseTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

# Internal imports
from app.config import settings, get_model_config
from app.tools.financial_data import get_financial_tools
from app.agents.market_analyst import MarketAnalystAgent
from app.agents.portfolio_manager import PortfolioManagerAgent
from app.agents.risk_assessor import RiskAssessorAgent
from app.agents.financial_educator import FinancialEducatorAgent

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State schema for the financial agent workflow."""
    messages: Annotated[List[BaseMessage], "The conversation messages"]
    current_task: str
    agent_outputs: Dict[str, Any]
    tools_used: List[str]
    user_context: Dict[str, Any]
    analysis_complete: bool
    needs_human_review: bool
    confidence_score: float


class FinancialSpecialistAgent:
    """
    Main Financial Specialist AI Agent that orchestrates multiple specialized agents
    using LangGraph for complex financial analysis and question-answering.
    """
    
    def __init__(self):
        """Initialize the Financial Specialist Agent."""
        self.model_config = get_model_config()
        self.llm = self._initialize_llm()
        self.tools = get_financial_tools()
        self.memory = ConversationBufferWindowMemory(
            k=settings.memory.max_conversation_history,
            return_messages=True
        )
        
        # Initialize specialized agents
        self.market_analyst = MarketAnalystAgent(self.llm)
        self.portfolio_manager = PortfolioManagerAgent(self.llm)
        self.risk_assessor = RiskAssessorAgent(self.llm)
        self.financial_educator = FinancialEducatorAgent(self.llm)
        
        # Initialize the workflow graph
        self.workflow = self._create_workflow()
        
        logger.info("Financial Specialist Agent initialized successfully")
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the language model with proper configuration."""
        return ChatOpenAI(
            model=settings.model.default_model,
            temperature=self.model_config["temperature"],
            max_tokens=self.model_config["max_tokens"],
            openai_api_key=settings.api_keys.openai_api_key,
        )
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for financial analysis."""
        workflow = StateGraph(AgentState)
        
        # Add nodes for different stages
        workflow.add_node("classifier", self._classify_query)
        workflow.add_node("market_analysis", self._market_analysis)
        workflow.add_node("portfolio_analysis", self._portfolio_analysis)
        workflow.add_node("risk_analysis", self._risk_analysis)
        workflow.add_node("education", self._financial_education)
        workflow.add_node("synthesis", self._synthesize_response)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Define the workflow edges
        workflow.set_entry_point("classifier")
        
        # Classifier decides which agent(s) to use
        workflow.add_conditional_edges(
            "classifier",
            self._route_query,
            {
                "market_analysis": "market_analysis",
                "portfolio_analysis": "portfolio_analysis",
                "risk_analysis": "risk_analysis",
                "education": "education",
                "tools": "tools"
            }
        )
        
        # Each analysis node can use tools or go to synthesis
        for node in ["market_analysis", "portfolio_analysis", "risk_analysis", "education"]:
            workflow.add_conditional_edges(
                node,
                self._needs_tools,
                {
                    "tools": "tools",
                    "synthesis": "synthesis"
                }
            )
        
        # Tools can lead back to any analysis or synthesis
        workflow.add_conditional_edges(
            "tools",
            self._route_after_tools,
            {
                "market_analysis": "market_analysis",
                "portfolio_analysis": "portfolio_analysis", 
                "risk_analysis": "risk_analysis",
                "education": "education",
                "synthesis": "synthesis"
            }
        )
        
        # Synthesis always ends
        workflow.add_edge("synthesis", END)
        
        return workflow.compile()
    
    def _classify_query(self, state: AgentState) -> AgentState:
        """Classify the user query to determine which agent(s) should handle it."""
        last_message = state["messages"][-1].content if state["messages"] else ""
        
        classifier_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial query classifier. Analyze the user's query and determine which type of financial analysis is needed.

Categories:
- market_analysis: Stock analysis, market trends, sector performance, company research
- portfolio_analysis: Portfolio optimization, asset allocation, investment strategies
- risk_analysis: Risk assessment, volatility analysis, scenario analysis
- education: Financial concept explanations, how-to guides, general education
- tools: Direct data requests (prices, company info, market data)

Respond with just the category name."""),
            ("human", "{query}")
        ])
        
        response = self.llm.invoke(classifier_prompt.format_messages(query=last_message))
        task_type = response.content.strip().lower()
        
        state["current_task"] = task_type
        state["agent_outputs"] = {}
        state["tools_used"] = []
        state["analysis_complete"] = False
        state["confidence_score"] = 0.0
        
        logger.info(f"Query classified as: {task_type}")
        return state
    
    def _route_query(self, state: AgentState) -> str:
        """Route the query to the appropriate agent based on classification."""
        task_type = state["current_task"]
        
        routing_map = {
            "market_analysis": "market_analysis",
            "portfolio_analysis": "portfolio_analysis", 
            "risk_analysis": "risk_analysis",
            "education": "education",
            "tools": "tools"
        }
        
        return routing_map.get(task_type, "education")
    
    def _market_analysis(self, state: AgentState) -> AgentState:
        """Perform market analysis using the Market Analyst agent."""
        try:
            query = state["messages"][-1].content
            analysis = self.market_analyst.analyze(query, context=state.get("user_context", {}))
            
            state["agent_outputs"]["market_analysis"] = analysis
            state["confidence_score"] = max(state["confidence_score"], analysis.get("confidence", 0.7))
            
            logger.info("Market analysis completed")
            return state
            
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            state["agent_outputs"]["market_analysis"] = {
                "error": str(e),
                "analysis": "Unable to complete market analysis due to technical issues."
            }
            return state
    
    def _portfolio_analysis(self, state: AgentState) -> AgentState:
        """Perform portfolio analysis using the Portfolio Manager agent."""
        try:
            query = state["messages"][-1].content
            analysis = self.portfolio_manager.analyze(query, context=state.get("user_context", {}))
            
            state["agent_outputs"]["portfolio_analysis"] = analysis
            state["confidence_score"] = max(state["confidence_score"], analysis.get("confidence", 0.7))
            
            logger.info("Portfolio analysis completed")
            return state
            
        except Exception as e:
            logger.error(f"Error in portfolio analysis: {e}")
            state["agent_outputs"]["portfolio_analysis"] = {
                "error": str(e),
                "analysis": "Unable to complete portfolio analysis due to technical issues."
            }
            return state
    
    def _risk_analysis(self, state: AgentState) -> AgentState:
        """Perform risk analysis using the Risk Assessor agent."""
        try:
            query = state["messages"][-1].content
            analysis = self.risk_assessor.analyze(query, context=state.get("user_context", {}))
            
            state["agent_outputs"]["risk_analysis"] = analysis
            state["confidence_score"] = max(state["confidence_score"], analysis.get("confidence", 0.7))
            
            logger.info("Risk analysis completed")
            return state
            
        except Exception as e:
            logger.error(f"Error in risk analysis: {e}")
            state["agent_outputs"]["risk_analysis"] = {
                "error": str(e),
                "analysis": "Unable to complete risk analysis due to technical issues."
            }
            return state
    
    def _financial_education(self, state: AgentState) -> AgentState:
        """Provide financial education using the Financial Educator agent."""
        try:
            query = state["messages"][-1].content
            education = self.financial_educator.educate(query, context=state.get("user_context", {}))
            
            state["agent_outputs"]["education"] = education
            state["confidence_score"] = max(state["confidence_score"], education.get("confidence", 0.8))
            
            logger.info("Financial education completed")
            return state
            
        except Exception as e:
            logger.error(f"Error in financial education: {e}")
            state["agent_outputs"]["education"] = {
                "error": str(e),
                "content": "Unable to provide educational content due to technical issues."
            }
            return state
    
    def _needs_tools(self, state: AgentState) -> str:
        """Determine if tools are needed for the current analysis."""
        # Check if any agent requested tool usage
        for output in state["agent_outputs"].values():
            if isinstance(output, dict) and output.get("needs_tools", False):
                return "tools"
        
        # If we haven't used any tools yet and it's a data-heavy query, use tools
        if not state["tools_used"] and state["current_task"] in ["market_analysis", "portfolio_analysis"]:
            return "tools"
        
        return "synthesis"
    
    def _route_after_tools(self, state: AgentState) -> str:
        """Route back to appropriate analysis after tool usage."""
        if not state.get("analysis_complete", False):
            return state["current_task"]
        return "synthesis"
    
    def _synthesize_response(self, state: AgentState) -> AgentState:
        """Synthesize the final response from all agent outputs."""
        try:
            synthesis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a financial specialist synthesizing analysis from multiple expert agents. 
                
Create a comprehensive, well-structured response that:
1. Directly addresses the user's question
2. Integrates insights from all available analyses
3. Provides clear, actionable recommendations
4. Includes appropriate disclaimers
5. Uses professional but accessible language

Available agent outputs: {agent_outputs}
Tools used: {tools_used}
Confidence score: {confidence}

Format your response as a financial expert would, with clear sections and bullet points where appropriate."""),
                ("human", "{original_query}")
            ])
            
            original_query = state["messages"][-1].content if state["messages"] else ""
            
            response = self.llm.invoke(synthesis_prompt.format_messages(
                agent_outputs=json.dumps(state["agent_outputs"], indent=2),
                tools_used=", ".join(state["tools_used"]),
                confidence=state["confidence_score"],
                original_query=original_query
            ))
            
            # Add the synthesized response to messages
            state["messages"].append(AIMessage(content=response.content))
            state["analysis_complete"] = True
            
            # Determine if human review is needed
            state["needs_human_review"] = (
                state["confidence_score"] < 0.6 or 
                any("error" in str(output) for output in state["agent_outputs"].values())
            )
            
            logger.info(f"Response synthesis completed with confidence: {state['confidence_score']}")
            return state
            
        except Exception as e:
            logger.error(f"Error in response synthesis: {e}")
            error_response = AIMessage(content=f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try rephrasing your question or contact support if the issue persists.")
            state["messages"].append(error_response)
            state["analysis_complete"] = True
            state["needs_human_review"] = True
            return state
    
    def process_query(self, query: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a financial query and return a comprehensive response.
        
        Args:
            query: The user's financial question or request
            user_context: Optional context about the user (risk tolerance, goals, etc.)
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            # Create initial state
            initial_state = AgentState(
                messages=[HumanMessage(content=query)],
                current_task="",
                agent_outputs={},
                tools_used=[],
                user_context=user_context or {},
                analysis_complete=False,
                needs_human_review=False,
                confidence_score=0.0
            )
            
            # Execute the workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Extract the response
            response_message = final_state["messages"][-1]
            
            return {
                "response": response_message.content,
                "confidence": final_state["confidence_score"],
                "needs_human_review": final_state["needs_human_review"],
                "agent_outputs": final_state["agent_outputs"],
                "tools_used": final_state["tools_used"],
                "task_type": final_state["current_task"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again or rephrase your question.",
                "confidence": 0.0,
                "needs_human_review": True,
                "agent_outputs": {},
                "tools_used": [],
                "task_type": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        try:
            messages = self.memory.chat_memory.messages
            return [
                {
                    "type": msg.__class__.__name__,
                    "content": msg.content,
                    "timestamp": getattr(msg, 'timestamp', datetime.now().isoformat())
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return []
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        try:
            self.memory.clear()
            logger.info("Conversation history cleared")
        except Exception as e:
            logger.error(f"Error clearing conversation history: {e}")
    
    def update_user_context(self, context: Dict[str, Any]) -> None:
        """Update user context for personalized responses."""
        # This would typically be stored in a database
        # For now, we'll just log the update
        logger.info(f"User context updated: {context}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the current system status and health metrics."""
        try:
            return {
                "status": "healthy",
                "model": settings.model.default_model,
                "tools_available": len(self.tools),
                "agents_available": 4,
                "memory_size": len(self.memory.chat_memory.messages) if hasattr(self.memory, 'chat_memory') else 0,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }


# Create a global instance for use across the application
financial_agent = None


def get_financial_agent() -> FinancialSpecialistAgent:
    """Get or create the global financial agent instance."""
    global financial_agent
    if financial_agent is None:
        financial_agent = FinancialSpecialistAgent()
    return financial_agent


def initialize_agent() -> FinancialSpecialistAgent:
    """Initialize and return a new financial agent instance."""
    return FinancialSpecialistAgent()


# Example usage and testing
if __name__ == "__main__":
    # Initialize the agent
    agent = FinancialSpecialistAgent()
    
    # Test queries
    test_queries = [
        "What's the current price of Apple stock and how has it performed this year?",
        "I have $50,000 to invest. Can you suggest a diversified portfolio for moderate risk tolerance?",
        "What are the main risks of investing in cryptocurrency?",
        "Can you explain what a P/E ratio is and why it's important?",
        "What's the current market sentiment and which sectors are performing well?"
    ]
    
    print("Testing Financial Specialist Agent...")
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test Query {i} ---")
        print(f"Query: {query}")
        
        result = agent.process_query(query)
        print(f"Response: {result['response'][:200]}...")
        print(f"Confidence: {result['confidence']}")
        print(f"Task Type: {result['task_type']}")
        print(f"Tools Used: {result['tools_used']}")
        print("-" * 50)