"""
Example Financial AI Agent Queries and Demonstrations
Shows various capabilities of the financial analysis system
"""

# Example queries for different use cases
EXAMPLE_QUERIES = {
    "stock_analysis": [
        "What's the current analysis of Apple (AAPL) stock?",
        "Can you analyze Tesla's financial performance and provide investment insights?",
        "Compare Microsoft and Google stocks for a long-term investment",
        "What are the key risks and opportunities for Amazon stock?",
        "Analyze the financial health of NVIDIA based on recent earnings"
    ],
    
    "market_overview": [
        "What's the current state of the stock market?",
        "How are different sectors performing this month?",
        "What are the major market trends I should be aware of?",
        "Can you provide an overview of the current market conditions?",
        "What's driving the market performance today?"
    ],
    
    "portfolio_management": [
        "How should I diversify my investment portfolio?",
        "What's a good asset allocation for a 30-year-old investor?",
        "How can I reduce risk in my current portfolio?",
        "What are some defensive stocks for uncertain times?",
        "Should I rebalance my portfolio given current market conditions?"
    ],
    
    "technical_analysis": [
        "What do the technical indicators suggest for Apple stock?",
        "Can you explain what RSI means and how to use it?",
        "What are the key support and resistance levels for Tesla?",
        "How do moving averages help in stock analysis?",
        "What technical patterns should I watch for in the market?"
    ],
    
    "economic_indicators": [
        "How do interest rates affect stock prices?",
        "What's the impact of inflation on my investments?",
        "How does GDP growth relate to market performance?",
        "What economic indicators should I monitor as an investor?",
        "How might Federal Reserve policy changes affect my portfolio?"
    ],
    
    "risk_management": [
        "How much should I invest in individual stocks vs ETFs?",
        "What's the appropriate position size for a risky investment?",
        "How can I protect my portfolio during market downturns?",
        "What are the main types of investment risks?",
        "Should I use stop-loss orders for my positions?"
    ],
    
    "fundamental_analysis": [
        "How do I analyze a company's financial statements?",
        "What's a good P/E ratio for technology stocks?",
        "How do I evaluate a company's debt levels?",
        "What financial metrics are most important for growth stocks?",
        "How do I assess management quality in a company?"
    ],
    
    "options_trading": [
        "Can you explain how call options work?",
        "What's the difference between buying and selling put options?",
        "How does implied volatility affect option prices?",
        "What are some basic option strategies for beginners?",
        "When should I consider using options in my portfolio?"
    ]
}

def demonstrate_capabilities():
    """Demonstrate the financial AI agent capabilities"""
    
    from src.financial_agent import financial_agent
    
    print("=== Financial AI Agent Demonstration ===\n")
    
    # Test each category with a sample question
    for category, queries in EXAMPLE_QUERIES.items():
        print(f"\n--- {category.replace('_', ' ').title()} ---")
        
        # Use the first query from each category
        sample_query = queries[0]
        print(f"Query: {sample_query}")
        
        try:
            response = financial_agent.ask(sample_query)
            print(f"Response: {response[:200]}...")  # First 200 characters
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 50)

def test_specific_stocks():
    """Test stock analysis for specific companies"""
    
    from src.data_sources import financial_data
    
    test_stocks = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    
    print("\n=== Stock Data Testing ===\n")
    
    for symbol in test_stocks:
        print(f"Testing {symbol}:")
        
        try:
            # Test basic data retrieval
            stock_data = financial_data.get_stock_data(symbol, "1mo")
            company_info = financial_data.get_company_info(symbol)
            technical_indicators = financial_data.calculate_technical_indicators(symbol)
            
            if not stock_data.empty:
                current_price = stock_data['Close'].iloc[-1]
                month_start = stock_data['Close'].iloc[0]
                performance = ((current_price / month_start) - 1) * 100
                
                print(f"  ✅ Current Price: ${current_price:.2f}")
                print(f"  ✅ 1-Month Performance: {performance:+.2f}%")
                print(f"  ✅ Company: {company_info.get('name', 'N/A')}")
                print(f"  ✅ Sector: {company_info.get('sector', 'N/A')}")
            else:
                print(f"  ❌ No data available")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()

def test_knowledge_base():
    """Test the financial knowledge base"""
    
    from src.knowledge_base import knowledge_base
    
    print("\n=== Knowledge Base Testing ===\n")
    
    # Test searches
    test_searches = [
        "P/E ratio",
        "risk management",
        "technical analysis",
        "portfolio diversification",
        "DCF analysis"
    ]
    
    for search_term in test_searches:
        print(f"Searching for: {search_term}")
        
        try:
            results = knowledge_base.search(search_term, n_results=2)
            if results:
                print(f"  ✅ Found relevant knowledge")
                print(f"  Preview: {results[:100]}...")
            else:
                print(f"  ⚠️ No results found")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()
    
    # Test categories
    try:
        categories = knowledge_base.get_all_categories()
        stats = knowledge_base.get_stats()
        
        print(f"Knowledge Base Stats:")
        print(f"  Total Documents: {stats.get('total_documents', 0)}")
        print(f"  Categories: {', '.join(categories)}")
        
    except Exception as e:
        print(f"Error getting knowledge base stats: {e}")

if __name__ == "__main__":
    print("Running Financial AI Agent Tests...\n")
    
    # Test individual components
    test_specific_stocks()
    test_knowledge_base()
    
    # Demonstrate full capabilities (requires API keys)
    try:
        demonstrate_capabilities()
    except Exception as e:
        print(f"Full demonstration requires API keys: {e}")
    
    print("\n=== Test Complete ===")
    print("To run the full application, use: streamlit run app.py")