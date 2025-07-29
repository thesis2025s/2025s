"""
Finance Specialist AI - Streamlit Application
Main web interface for the financial Q&A system.
"""

import streamlit as st
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import application modules
try:
    from app.agents.financial_agent import FinancialSpecialistAgent
    from app.memory.vector_store import get_vector_store
    from app.config import settings
except ImportError as e:
    logger.error(f"Import error: {e}")
    st.error(f"Application configuration error: {e}")
    st.stop()


# Page configuration
st.set_page_config(
    page_title="Finance Specialist AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e7d32 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f4e79;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .agent-response {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2e7d32;
        margin: 1rem 0;
    }
    
    .sidebar-content {
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    if "agent" not in st.session_state:
        try:
            st.session_state.agent = FinancialSpecialistAgent()
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            st.error(f"Failed to initialize AI agent: {e}")
            st.stop()
    
    if "vector_store" not in st.session_state:
        try:
            st.session_state.vector_store = get_vector_store()
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            st.warning(f"Vector store unavailable: {e}")
            st.session_state.vector_store = None
    
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {
            "investment_experience": "beginner",
            "risk_tolerance": "moderate",
            "investment_goals": [],
            "preferred_topics": []
        }


def display_header():
    """Display the application header."""
    st.markdown("""
    <div class="main-header">
        <h1>💰 Finance Specialist AI</h1>
        <p>Your Expert AI Assistant for Financial Analysis, Investment Guidance & Market Insights</p>
    </div>
    """, unsafe_allow_html=True)


def display_sidebar():
    """Display the sidebar with user controls and information."""
    with st.sidebar:
        st.markdown("## 🎛️ Controls")
        
        # Session management
        st.markdown("### Session Management")
        if st.button("🔄 New Session", help="Start a new conversation session"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.conversation_history = []
            st.rerun()
        
        if st.button("🗑️ Clear History", help="Clear conversation history"):
            st.session_state.conversation_history = []
            if st.session_state.vector_store:
                st.session_state.vector_store.clear_session_data(st.session_state.session_id)
            st.rerun()
        
        # User profile
        st.markdown("### 👤 User Profile")
        with st.expander("Investment Profile", expanded=False):
            st.session_state.user_profile["investment_experience"] = st.selectbox(
                "Investment Experience",
                ["beginner", "intermediate", "advanced", "professional"],
                index=["beginner", "intermediate", "advanced", "professional"].index(
                    st.session_state.user_profile["investment_experience"]
                )
            )
            
            st.session_state.user_profile["risk_tolerance"] = st.selectbox(
                "Risk Tolerance",
                ["conservative", "moderate", "aggressive"],
                index=["conservative", "moderate", "aggressive"].index(
                    st.session_state.user_profile["risk_tolerance"]
                )
            )
            
            # Investment goals
            goal_options = [
                "retirement_planning", "wealth_building", "income_generation",
                "capital_preservation", "education_funding", "emergency_fund"
            ]
            selected_goals = st.multiselect(
                "Investment Goals",
                goal_options,
                default=st.session_state.user_profile["investment_goals"]
            )
            st.session_state.user_profile["investment_goals"] = selected_goals
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Market Overview"):
                st.session_state.quick_query = "Give me a comprehensive market overview for today"
        
        with col2:
            if st.button("📈 Top Stocks"):
                st.session_state.quick_query = "What are the top performing stocks today?"
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("💡 Investment Tips"):
                st.session_state.quick_query = "Give me 5 investment tips for my profile"
        
        with col4:
            if st.button("🎯 Portfolio Review"):
                st.session_state.quick_query = "How should I review my investment portfolio?"
        
        # Agent selection
        st.markdown("### 🤖 Specialist Mode")
        agent_mode = st.selectbox(
            "Choose Specialist",
            ["auto", "market_analyst", "portfolio_manager", "risk_assessor", "financial_educator"],
            format_func=lambda x: {
                "auto": "🎯 Auto (Best Agent)",
                "market_analyst": "📊 Market Analyst",
                "portfolio_manager": "💼 Portfolio Manager",
                "risk_assessor": "⚠️ Risk Assessor",
                "financial_educator": "🎓 Financial Educator"
            }[x]
        )
        st.session_state.agent_mode = agent_mode
        
        # System stats
        if st.session_state.vector_store:
            with st.expander("📈 System Stats", expanded=False):
                try:
                    stats = st.session_state.vector_store.get_stats()
                    st.metric("Conversations", stats.get("conversations", 0))
                    st.metric("Knowledge Items", stats.get("knowledge_items", 0))
                    st.metric("Document Chunks", stats.get("document_chunks", 0))
                except Exception as e:
                    st.error(f"Stats unavailable: {e}")


def display_conversation_history():
    """Display the conversation history."""
    if st.session_state.conversation_history:
        st.markdown("## 💬 Conversation History")
        
        for i, exchange in enumerate(st.session_state.conversation_history):
            with st.container():
                # User message
                st.markdown(f"**👤 You ({exchange['timestamp']}):**")
                st.markdown(exchange["user_query"])
                
                # AI response
                st.markdown("**🤖 Finance Specialist AI:**")
                st.markdown(f'<div class="agent-response">{exchange["ai_response"]}</div>', 
                           unsafe_allow_html=True)
                
                # Additional info if available
                if exchange.get("agent_used"):
                    st.caption(f"*Specialist: {exchange['agent_used']}*")
                
                if exchange.get("confidence"):
                    confidence = exchange["confidence"]
                    confidence_color = "green" if confidence > 0.7 else "orange" if confidence > 0.5 else "red"
                    st.caption(f"*Confidence: <span style='color:{confidence_color}'>{confidence:.1%}</span>*", 
                              unsafe_allow_html=True)
                
                st.divider()


def process_user_query(query: str) -> Dict[str, Any]:
    """Process user query and get AI response."""
    try:
        # Prepare context from user profile
        context = {
            "user_profile": st.session_state.user_profile,
            "session_id": st.session_state.session_id,
            "agent_mode": getattr(st.session_state, "agent_mode", "auto")
        }
        
        # Get relevant conversation history
        if st.session_state.vector_store:
            try:
                relevant_conversations = st.session_state.vector_store.retrieve_relevant_conversations(
                    query, 
                    st.session_state.session_id,
                    limit=3
                )
                context["relevant_history"] = relevant_conversations
            except Exception as e:
                logger.warning(f"Could not retrieve conversation history: {e}")
        
        # Process query with agent
        with st.spinner("🤖 Finance Specialist AI is analyzing your query..."):
            result = st.session_state.agent.process_query(query, context)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        logger.error(traceback.format_exc())
        return {
            "response": f"I apologize, but I encountered an error while processing your query: {str(e)}",
            "confidence": 0.0,
            "agent_used": "error_handler",
            "error": str(e)
        }


def save_conversation(user_query: str, ai_response: str, metadata: Dict[str, Any]):
    """Save conversation to memory."""
    if st.session_state.vector_store:
        try:
            st.session_state.vector_store.store_conversation(
                user_query,
                ai_response,
                st.session_state.session_id,
                metadata
            )
        except Exception as e:
            logger.warning(f"Could not save conversation: {e}")


def display_main_interface():
    """Display the main chat interface."""
    st.markdown("## 💬 Ask Your Financial Question")
    
    # Handle quick queries from sidebar
    initial_query = ""
    if hasattr(st.session_state, "quick_query"):
        initial_query = st.session_state.quick_query
        delattr(st.session_state, "quick_query")
    
    # Input form
    with st.form("query_form", clear_on_submit=True):
        user_query = st.text_area(
            "What would you like to know about finance, investments, or markets?",
            height=100,
            placeholder="Example: What's the best investment strategy for someone with moderate risk tolerance saving for retirement?",
            value=initial_query
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            submit_button = st.form_submit_button("🚀 Ask AI", use_container_width=True)
        with col2:
            example_button = st.form_submit_button("💡 Example", use_container_width=True)
    
    # Handle example button
    if example_button:
        example_queries = [
            "What are the key factors to consider when building a diversified portfolio?",
            "How do interest rates affect different types of investments?",
            "What's the difference between growth and value investing strategies?",
            "How should I evaluate a company's financial health before investing?",
            "What are the tax implications of different investment accounts?"
        ]
        import random
        user_query = random.choice(example_queries)
        submit_button = True
    
    # Process query
    if submit_button and user_query.strip():
        # Add user message to history immediately for better UX
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Get AI response
        result = process_user_query(user_query)
        
        # Extract response details
        ai_response = result.get("response", "I apologize, but I couldn't generate a response.")
        confidence = result.get("confidence", 0.0)
        agent_used = result.get("agent_used", "unknown")
        
        # Add to conversation history
        exchange = {
            "timestamp": timestamp,
            "user_query": user_query,
            "ai_response": ai_response,
            "confidence": confidence,
            "agent_used": agent_used
        }
        st.session_state.conversation_history.append(exchange)
        
        # Save to vector store
        save_conversation(user_query, ai_response, result)
        
        # Rerun to show updated conversation
        st.rerun()


def display_disclaimer():
    """Display important disclaimer."""
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ Important Disclaimer</h4>
        <p>This AI assistant provides general financial information and educational content for informational purposes only. 
        It is not personalized financial advice and should not be considered as investment, tax, or legal advice. 
        Always consult with qualified financial professionals before making investment decisions.</p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application function."""
    try:
        # Initialize application
        initialize_session_state()
        
        # Display header
        display_header()
        
        # Display disclaimer
        display_disclaimer()
        
        # Create layout
        sidebar_col = st.sidebar
        
        # Display sidebar
        display_sidebar()
        
        # Main content area
        main_col1, main_col2 = st.columns([2, 1])
        
        with main_col1:
            # Main chat interface
            display_main_interface()
            
            # Show conversation history
            display_conversation_history()
        
        with main_col2:
            # Additional features panel
            st.markdown("## 📋 Features")
            
            st.markdown("""
            ### Available Specialists:
            - **📊 Market Analyst**: Stock analysis, market trends
            - **💼 Portfolio Manager**: Asset allocation, optimization  
            - **⚠️ Risk Assessor**: Risk analysis, scenario planning
            - **🎓 Financial Educator**: Concept explanations, learning
            
            ### Key Capabilities:
            - Real-time market data analysis
            - Portfolio optimization recommendations
            - Risk assessment and management
            - Financial education and explanations
            - Investment strategy guidance
            - Economic indicator analysis
            """)
            
            # File upload feature
            st.markdown("### 📄 Document Analysis")
            uploaded_file = st.file_uploader(
                "Upload financial documents for analysis",
                type=['pdf', 'txt', 'csv', 'xlsx'],
                help="Upload financial statements, reports, or data for AI analysis"
            )
            
            if uploaded_file is not None:
                with st.spinner("Processing document..."):
                    try:
                        # Read file content
                        if uploaded_file.type == "text/plain":
                            content = str(uploaded_file.read(), "utf-8")
                        elif uploaded_file.type == "application/pdf":
                            st.info("PDF processing not yet implemented. Please use text files.")
                            content = None
                        else:
                            st.info(f"File type {uploaded_file.type} not yet supported.")
                            content = None
                        
                        if content and st.session_state.vector_store:
                            # Store document
                            st.session_state.vector_store.store_document(
                                content,
                                uploaded_file.name,
                                uploaded_file.type
                            )
                            st.success(f"Document '{uploaded_file.name}' processed successfully!")
                            
                    except Exception as e:
                        st.error(f"Error processing document: {e}")
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        logger.error(traceback.format_exc())
        st.error(f"Application error: {e}")
        st.error("Please check your configuration and try again.")


if __name__ == "__main__":
    main()