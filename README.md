# 📈 Financial AI Agent

A comprehensive financial analysis and advisory system powered by AI and real-time market data. This system provides expert financial advice, market analysis, and investment insights through an intuitive web interface.

## 🌟 Features

### 💬 AI-Powered Financial Advisor
- **Expert Analysis**: GPT-4 powered financial expert with deep market knowledge
- **Real-time Data**: Integration with Yahoo Finance and Alpha Vantage APIs
- **Conversational Memory**: Maintains context across conversations
- **Risk Assessment**: Comprehensive risk analysis and management advice

### 📈 Market Data & Analytics
- **Live Stock Data**: Real-time stock prices, charts, and technical indicators
- **Sector Analysis**: Performance tracking across all major market sectors
- **Technical Indicators**: RSI, Moving Averages, Support/Resistance levels
- **Company Fundamentals**: Financial statements, ratios, and business metrics

### 📚 Knowledge Base (RAG)
- **Financial Concepts**: Comprehensive database of financial knowledge
- **Smart Search**: Vector-based semantic search for relevant information
- **Categories**: Organized by valuation, risk management, technical analysis, etc.
- **Expandable**: Add custom knowledge and expertise

### 🎯 Key Capabilities
- Stock analysis and investment recommendations
- Portfolio optimization and diversification strategies
- Risk management and hedging techniques
- Economic indicator analysis and market trend identification
- Financial planning and goal-setting guidance

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (required)
- Alpha Vantage API key (optional, for enhanced economic data)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd financial-ai-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

4. **Launch the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the web interface**
   Open your browser to `http://localhost:8501`

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (enhances economic data features)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
ALPHA_VANTAGE_BASE_URL=https://www.alphavantage.co

# App Settings
DEBUG=False
LOG_LEVEL=INFO
MAX_TOKENS=4000
TEMPERATURE=0.1
```

### Getting API Keys

1. **OpenAI API Key** (Required)
   - Visit [OpenAI API](https://platform.openai.com/api-keys)
   - Create an account and generate an API key
   - Add billing information for usage

2. **Alpha Vantage API Key** (Optional)
   - Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
   - Sign up for a free account
   - Get your API key from the dashboard

## 📖 Usage Examples

### Basic Stock Analysis
```python
from src.financial_agent import financial_agent

# Analyze a specific stock
response = financial_agent.ask("What's your analysis of Apple (AAPL) stock?")
print(response)

# Get market overview
response = financial_agent.ask("How is the overall market performing today?")
print(response)
```

### Portfolio Optimization
```python
# Get portfolio advice
response = financial_agent.ask(
    "I'm 30 years old with $50k to invest. How should I diversify my portfolio?"
)
print(response)
```

### Technical Analysis
```python
# Technical indicators analysis
response = financial_agent.ask(
    "What do the technical indicators suggest for Tesla stock?"
)
print(response)
```

## 🏗️ Architecture

### System Components

```
Financial AI Agent
├── Web Interface (Streamlit)
│   ├── Chat Interface
│   ├── Market Data Dashboard
│   ├── Knowledge Base Browser
│   └── System Status
├── AI Agent Core (LangChain)
│   ├── Financial Tools
│   ├── Memory Management
│   └── Response Generation
├── Data Sources
│   ├── Yahoo Finance (yfinance)
│   ├── Alpha Vantage API
│   └── Real-time Market Data
└── Knowledge Base (RAG)
    ├── Vector Database (ChromaDB)
    ├── Financial Concepts
    └── Semantic Search
```

### Technology Stack

- **AI/ML**: OpenAI GPT-4, LangChain, Sentence Transformers
- **Data**: Yahoo Finance, Alpha Vantage, Pandas, NumPy
- **Database**: ChromaDB (Vector Database)
- **Frontend**: Streamlit, Plotly, HTML/CSS
- **Backend**: FastAPI (optional), Python
- **Deployment**: Docker, Cloud platforms

## 📊 Features Deep Dive

### AI Chat Assistant
- **Natural Language**: Ask questions in plain English
- **Context Awareness**: Remembers previous conversation
- **Expert Knowledge**: Financial expertise built-in
- **Data Integration**: Pulls real-time data for analysis

### Market Data Integration
- **Real-time Prices**: Live stock and ETF data
- **Technical Analysis**: 20+ technical indicators
- **Sector Performance**: Track all major market sectors
- **Historical Data**: Access to years of market history

### Knowledge Base (RAG)
- **Vector Search**: Semantic similarity matching
- **Financial Concepts**: 100+ financial topics covered
- **Custom Content**: Add your own financial knowledge
- **Smart Context**: Relevant information for each query

## 🔍 Example Queries

The system can handle various types of financial questions:

### Stock Analysis
- "What's your analysis of Microsoft stock?"
- "Should I buy Tesla at current prices?"
- "Compare Apple and Google for long-term investment"

### Portfolio Management
- "How should I diversify a $100k portfolio?"
- "What's the optimal asset allocation for my age?"
- "How can I reduce portfolio risk?"

### Market Analysis
- "What's driving today's market movement?"
- "How are tech stocks performing this quarter?"
- "What sectors are showing strength?"

### Economic Insights
- "How will rising interest rates affect my investments?"
- "What's the impact of inflation on stock prices?"
- "Should I be concerned about recession indicators?"

## 🛡️ Risk Management

### Data Security
- API keys stored securely in environment variables
- No financial data stored permanently
- Local vector database for knowledge base

### Investment Disclaimers
- **Educational Purpose**: System is for informational use only
- **Not Financial Advice**: Always consult qualified professionals
- **Risk Warning**: All investments carry risk of loss
- **Past Performance**: Does not guarantee future results

## 🧪 Testing

Run the test suite to verify system functionality:

```bash
python examples/example_queries.py
```

This will test:
- Data source connectivity
- Knowledge base functionality
- AI agent responses
- System integration

## 📈 Performance

### Response Times
- **Stock Data**: < 2 seconds
- **AI Analysis**: 3-10 seconds
- **Knowledge Search**: < 1 second
- **Market Overview**: 5-15 seconds

### Accuracy
- **Market Data**: Real-time from Yahoo Finance
- **Financial Knowledge**: Curated expert content
- **AI Responses**: GPT-4 with financial prompting

## 🔄 Updates & Maintenance

### Regular Updates
- **Market Data**: Real-time updates
- **Knowledge Base**: Periodic content updates
- **AI Models**: Latest OpenAI model versions
- **Dependencies**: Security and feature updates

### Monitoring
- System health checks in web interface
- API connectivity status
- Performance metrics tracking

## 🤝 Contributing

We welcome contributions to improve the Financial AI Agent:

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests if needed**
5. **Submit a pull request**

### Areas for Contribution
- Additional financial data sources
- Enhanced technical analysis tools
- New knowledge base content
- UI/UX improvements
- Performance optimizations

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support, questions, or feature requests:

1. **Documentation**: Check this README and code comments
2. **Issues**: Open a GitHub issue for bugs or features
3. **Discussions**: Use GitHub Discussions for questions

## 🚨 Important Notes

### API Rate Limits
- **Yahoo Finance**: No strict limits, but avoid excessive requests
- **Alpha Vantage**: 5 requests/minute (free tier)
- **OpenAI**: Depends on your subscription plan

### System Requirements
- **Memory**: 4GB+ RAM recommended
- **Storage**: 1GB+ for dependencies and data
- **Network**: Stable internet for real-time data

### Production Deployment
For production use:
- Implement proper error handling
- Add authentication and user management
- Set up monitoring and logging
- Consider scaling and load balancing
- Implement data caching strategies

---

**Built with ❤️ for the financial community**

*Remember: This system is designed to enhance your financial knowledge and decision-making, but should never replace professional financial advice. Always do your own research and consult with qualified financial professionals before making investment decisions.*