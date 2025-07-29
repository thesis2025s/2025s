# Finance Specialist AI - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.9+ installed
- OpenAI API key (required)
- Optional: Other financial API keys for enhanced features

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd finance-specialist-ai

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env  # or use your preferred editor
```

**Required API Key:**
- `OPENAI_API_KEY`: Get from [OpenAI](https://platform.openai.com/api-keys)

**Optional API Keys (for enhanced features):**
- `ALPHA_VANTAGE_API_KEY`: Free from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
- `FMP_API_KEY`: From [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs)
- `FRED_API_KEY`: From [FRED Economic Data](https://fred.stlouisfed.org/docs/api/api_key.html)

### 3. Run the Application

#### Option A: Using the launcher script (Recommended)
```bash
python run.py
```

#### Option B: Direct Streamlit command
```bash
streamlit run app.py
```

### 4. Access the Application

Open your browser and go to: **http://localhost:8501**

## 🐳 Docker Deployment

### Quick Docker Run
```bash
# Build the image
docker build -t finance-ai .

# Run the container
docker run -p 8501:8501 --env-file .env finance-ai
```

### Docker Compose (Recommended for production)
```bash
# Basic deployment
docker-compose up -d

# With production services (PostgreSQL, Redis, Nginx)
docker-compose --profile production up -d
```

## 🔧 Configuration Options

### User Profile Settings
- **Investment Experience**: Beginner, Intermediate, Advanced, Professional
- **Risk Tolerance**: Conservative, Moderate, Aggressive
- **Investment Goals**: Retirement, Wealth Building, Income Generation, etc.

### AI Specialist Modes
- **Auto**: Automatically selects the best specialist for your query
- **Market Analyst**: Stock analysis and market trends
- **Portfolio Manager**: Asset allocation and optimization
- **Risk Assessor**: Risk analysis and scenario planning
- **Financial Educator**: Concept explanations and learning

## 📝 Example Queries

Try these sample questions to get started:

**Market Analysis:**
- "What's the current market outlook for tech stocks?"
- "Analyze the performance of AAPL vs MSFT this year"
- "What sectors are performing well in the current market?"

**Investment Strategy:**
- "What's the best investment strategy for a 30-year-old saving for retirement?"
- "How should I diversify my portfolio with $50,000 to invest?"
- "What are the pros and cons of dollar-cost averaging?"

**Risk Assessment:**
- "What are the main risks in my current portfolio allocation?"
- "How would a recession affect different asset classes?"
- "What's the optimal portfolio allocation for my risk tolerance?"

**Financial Education:**
- "Explain the difference between growth and value investing"
- "What are compound interest and how does it work?"
- "How do interest rates affect bond prices?"

## 🔒 Security Features

- **Rate Limiting**: Prevents abuse with configurable limits
- **Input Validation**: Sanitizes and validates all user inputs
- **Session Management**: Secure session handling
- **Content Filtering**: Blocks malicious content and injection attempts

## 🛠️ Advanced Features

### Document Upload
- Upload financial documents (PDF, CSV, TXT) for AI analysis
- Supported formats: Financial statements, reports, data files

### Memory System
- Conversation history with semantic search
- Persistent knowledge base
- Document storage and retrieval

### API Integration
- Real-time market data
- Economic indicators
- News sentiment analysis
- Company fundamentals

## 📊 Production Deployment

### Environment Variables for Production
```bash
# Model Configuration
DEFAULT_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.1
MAX_TOKENS=4000

# Database (optional)
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=your-domain.com,localhost

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/finance-ai.log
```

### Scaling Considerations
- Use PostgreSQL for production database
- Implement Redis for caching and session storage
- Use Nginx as reverse proxy
- Consider horizontal scaling with multiple containers

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
1. Check your `.env` file has the required API keys
2. Ensure Python 3.9+ is installed
3. Verify all dependencies are installed: `pip install -r requirements.txt`

**API Errors:**
1. Verify your OpenAI API key is valid and has credits
2. Check API rate limits and quotas
3. Ensure network connectivity to external APIs

**Memory Issues:**
1. Check available disk space for vector database
2. Clear conversation history if needed
3. Monitor memory usage with large document uploads

**Performance Issues:**
1. Use production deployment with PostgreSQL and Redis
2. Optimize API call frequency
3. Consider upgrading to more powerful hardware

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review application logs in the `logs/` directory
3. Ensure all environment variables are properly configured
4. Test with simple queries first

## 🎯 Next Steps

1. **Customize the AI**: Modify prompts and agent behaviors in `app/agents/`
2. **Add Tools**: Extend functionality by adding new tools in `app/tools/`
3. **Enhance UI**: Customize the Streamlit interface in `app.py`
4. **Production Deploy**: Use Docker Compose with production profile

Happy investing with AI! 💰📈