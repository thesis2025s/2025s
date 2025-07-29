"""
Financial AI Agent - Streamlit Web Application
A comprehensive financial Q&A system with real-time data integration
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
from config import settings
from src.financial_agent import financial_agent
from src.data_sources import financial_data
from src.knowledge_base import knowledge_base

# Page configuration
st.set_page_config(
    page_title="Financial AI Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">📈 Financial AI Agent</h1>', unsafe_allow_html=True)
    st.markdown("**Your Expert Financial Advisor powered by AI and Real-time Market Data**")
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ Tools & Settings")
        
        # API Key check
        if not settings.openai_api_key:
            st.error("⚠️ OpenAI API key not configured. Please add your API key to the .env file.")
            st.stop()
        
        # Quick actions
        st.subheader("Quick Actions")
        
        if st.button("📊 Market Overview", use_container_width=True):
            st.session_state.quick_action = "market_overview"
        
        if st.button("🔍 Stock Analysis", use_container_width=True):
            st.session_state.quick_action = "stock_analysis"
        
        if st.button("📰 Economic Data", use_container_width=True):
            st.session_state.quick_action = "economic_data"
        
        # Settings
        st.subheader("Settings")
        
        # Temperature setting
        temperature = st.slider(
            "AI Response Creativity",
            min_value=0.0,
            max_value=1.0,
            value=settings.temperature,
            step=0.1,
            help="Lower values make responses more focused and deterministic"
        )
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            financial_agent.clear_memory()
            if 'messages' in st.session_state:
                del st.session_state.messages
            st.success("Conversation cleared!")
            st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 AI Chat", "📈 Market Data", "📚 Knowledge Base", "ℹ️ About"])
    
    with tab1:
        chat_interface()
    
    with tab2:
        market_data_interface()
    
    with tab3:
        knowledge_base_interface()
    
    with tab4:
        about_interface()

def chat_interface():
    """Chat interface with the financial AI agent"""
    
    st.header("💬 Chat with Financial AI")
    st.markdown("Ask me anything about finance, investments, market analysis, or economic trends!")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your Financial AI Agent. I can help you with:\n\n"
                          "• Stock analysis and investment advice\n"
                          "• Market trends and economic data\n"
                          "• Portfolio optimization strategies\n"
                          "• Risk management techniques\n"
                          "• Financial planning guidance\n\n"
                          "What would you like to know about?"
            }
        ]
    
    # Handle quick actions
    if hasattr(st.session_state, 'quick_action'):
        quick_action = st.session_state.quick_action
        del st.session_state.quick_action
        
        if quick_action == "market_overview":
            query = "Can you provide a comprehensive market overview including major indices and sector performance?"
        elif quick_action == "stock_analysis":
            query = "I need help analyzing a stock. What information do you need from me?"
        elif quick_action == "economic_data":
            query = "What are the current economic indicators I should be aware of?"
        else:
            query = None
        
        if query:
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("Analyzing..."):
                response = financial_agent.ask(query)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask your financial question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = financial_agent.ask(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

def market_data_interface():
    """Market data visualization interface"""
    
    st.header("📈 Real-time Market Data")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Stock Analysis")
        
        # Stock symbol input
        symbol = st.text_input(
            "Enter Stock Symbol",
            value="AAPL",
            help="Enter a valid stock symbol (e.g., AAPL, MSFT, GOOGL)"
        ).upper()
        
        if symbol:
            with st.spinner(f"Loading data for {symbol}..."):
                # Get stock data
                stock_data = financial_data.get_stock_data(symbol, "1y")
                company_info = financial_data.get_company_info(symbol)
                technical_indicators = financial_data.calculate_technical_indicators(symbol)
                
                if not stock_data.empty:
                    # Price chart
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=stock_data.index,
                        y=stock_data['Close'],
                        mode='lines',
                        name='Close Price',
                        line=dict(color='#1f77b4', width=2)
                    ))
                    
                    fig.update_layout(
                        title=f"{symbol} - 1 Year Price Chart",
                        xaxis_title="Date",
                        yaxis_title="Price ($)",
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Volume chart
                    fig_volume = go.Figure()
                    fig_volume.add_trace(go.Bar(
                        x=stock_data.index,
                        y=stock_data['Volume'],
                        name='Volume',
                        marker_color='rgba(31, 119, 180, 0.6)'
                    ))
                    
                    fig_volume.update_layout(
                        title=f"{symbol} - Trading Volume",
                        xaxis_title="Date",
                        yaxis_title="Volume",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_volume, use_container_width=True)
                
                else:
                    st.error(f"Could not retrieve data for {symbol}. Please check the symbol.")
    
    with col2:
        if symbol and not stock_data.empty:
            st.subheader("Key Metrics")
            
            # Current metrics
            current_price = technical_indicators.get('current_price', 0)
            year_start = stock_data['Close'].iloc[0]
            ytd_performance = ((current_price / year_start) - 1) * 100 if year_start else 0
            
            # Display metrics
            st.metric(
                label="Current Price",
                value=f"${current_price}",
                delta=f"{ytd_performance:.2f}% YTD"
            )
            
            st.metric(
                label="Market Cap",
                value=f"${company_info.get('marketCap', 0):,.0f}"
            )
            
            st.metric(
                label="P/E Ratio",
                value=f"{company_info.get('peRatio', 'N/A')}"
            )
            
            st.metric(
                label="Beta",
                value=f"{company_info.get('beta', 'N/A')}"
            )
            
            # Company info
            st.subheader("Company Info")
            st.write(f"**Name:** {company_info.get('name', 'N/A')}")
            st.write(f"**Sector:** {company_info.get('sector', 'N/A')}")
            st.write(f"**Industry:** {company_info.get('industry', 'N/A')}")
    
    # Market overview
    st.subheader("📊 Market Overview")
    
    with st.spinner("Loading market data..."):
        sector_performance = financial_data.get_sector_performance()
        
        if sector_performance:
            # Create sector performance chart
            sectors = list(sector_performance.keys())
            performances = [data['performance_1m'] for data in sector_performance.values()]
            
            fig_sectors = px.bar(
                x=sectors,
                y=performances,
                title="Sector Performance (1 Month)",
                labels={'x': 'Sector ETF', 'y': 'Performance (%)'},
                color=performances,
                color_continuous_scale='RdYlGn'
            )
            
            fig_sectors.update_layout(showlegend=False)
            st.plotly_chart(fig_sectors, use_container_width=True)

def knowledge_base_interface():
    """Knowledge base management interface"""
    
    st.header("📚 Financial Knowledge Base")
    st.markdown("Explore and manage the financial knowledge that enhances AI responses.")
    
    # Knowledge base stats
    stats = knowledge_base.get_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Documents", stats.get('total_documents', 0))
    with col2:
        st.metric("Categories", stats.get('category_count', 0))
    with col3:
        st.metric("System Status", "Active" if stats else "Error")
    
    # Search knowledge base
    st.subheader("🔍 Search Knowledge Base")
    search_query = st.text_input("Search for financial concepts...")
    
    if search_query:
        with st.spinner("Searching..."):
            results = knowledge_base.search(search_query, n_results=5)
            if results:
                st.markdown("### Search Results")
                st.markdown(results)
            else:
                st.info("No relevant results found.")
    
    # Browse by category
    st.subheader("📂 Browse by Category")
    categories = knowledge_base.get_all_categories()
    
    if categories:
        selected_category = st.selectbox("Select a category:", ["All"] + categories)
        
        if selected_category != "All":
            category_knowledge = knowledge_base.get_knowledge_by_category(selected_category)
            
            for item in category_knowledge:
                with st.expander(item['metadata'].get('title', 'Knowledge Item')):
                    st.markdown(item['content'])
    
    # Add new knowledge (for demo purposes)
    with st.expander("➕ Add New Knowledge"):
        st.markdown("*Note: This is a demonstration feature*")
        
        new_title = st.text_input("Title")
        new_category = st.text_input("Category")
        new_content = st.text_area("Content")
        
        if st.button("Add Knowledge") and new_title and new_content:
            metadata = {"title": new_title, "category": new_category}
            doc_id = knowledge_base.add_knowledge(new_content, metadata)
            if doc_id:
                st.success("Knowledge added successfully!")
            else:
                st.error("Failed to add knowledge.")

def about_interface():
    """About page with system information"""
    
    st.header("ℹ️ About Financial AI Agent")
    
    st.markdown("""
    ### 🎯 Overview
    
    This Financial AI Agent is a comprehensive financial analysis and advisory system that combines:
    
    - **Real-time Financial Data**: Integration with Yahoo Finance and Alpha Vantage APIs
    - **Advanced AI**: Powered by OpenAI's GPT models with financial expertise
    - **Knowledge Base**: RAG (Retrieval Augmented Generation) system with financial concepts
    - **Interactive Interface**: User-friendly Streamlit web application
    
    ### 🚀 Features
    
    #### 💬 AI Chat Assistant
    - Expert financial advice and analysis
    - Real-time market data integration
    - Conversational memory for context
    - Comprehensive risk assessments
    
    #### 📈 Market Data Analysis
    - Live stock prices and charts
    - Technical indicators (RSI, Moving Averages)
    - Sector performance analysis
    - Company fundamental data
    
    #### 📚 Knowledge Base
    - Financial concepts and definitions
    - Investment strategies and methodologies
    - Risk management principles
    - Market analysis techniques
    
    ### 🛠️ Technology Stack
    
    - **AI/ML**: OpenAI GPT-4, LangChain, Sentence Transformers
    - **Data Sources**: Yahoo Finance (yfinance), Alpha Vantage
    - **Vector Database**: ChromaDB for knowledge storage
    - **Frontend**: Streamlit with Plotly visualizations
    - **Analysis**: Pandas, NumPy, SciPy
    
    ### ⚠️ Important Disclaimers
    
    - This system is for educational and informational purposes only
    - Not intended as personalized financial advice
    - Always consult with qualified financial professionals
    - Past performance does not guarantee future results
    - All investments carry risk of loss
    
    ### 🔧 Configuration
    
    To set up this system:
    
    1. **API Keys**: Configure OpenAI and Alpha Vantage API keys in `.env`
    2. **Dependencies**: Install required packages from `requirements.txt`
    3. **Data Storage**: ChromaDB will create local storage automatically
    4. **Launch**: Run with `streamlit run app.py`
    
    ### 📊 System Status
    """)
    
    # System status checks
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("API Status")
        
        # OpenAI API
        if settings.openai_api_key:
            st.success("✅ OpenAI API: Configured")
        else:
            st.error("❌ OpenAI API: Not configured")
        
        # Alpha Vantage API
        if settings.alpha_vantage_api_key:
            st.success("✅ Alpha Vantage API: Configured")
        else:
            st.warning("⚠️ Alpha Vantage API: Not configured (optional)")
    
    with col2:
        st.subheader("System Components")
        
        try:
            # Test data sources
            test_data = financial_data.get_stock_data("AAPL", "5d")
            if not test_data.empty:
                st.success("✅ Financial Data: Working")
            else:
                st.error("❌ Financial Data: Error")
        except:
            st.error("❌ Financial Data: Error")
        
        try:
            # Test knowledge base
            stats = knowledge_base.get_stats()
            if stats:
                st.success("✅ Knowledge Base: Working")
            else:
                st.error("❌ Knowledge Base: Error")
        except:
            st.error("❌ Knowledge Base: Error")
    
    st.markdown("""
    ### 📞 Support
    
    For technical support or feature requests, please refer to the project documentation
    or contact the development team.
    """)

if __name__ == "__main__":
    main()