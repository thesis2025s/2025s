# 🚀 Quick Start Guide - Financial AI Agent

Get your Financial AI Agent up and running in 5 minutes!

## 📋 Prerequisites
- Python 3.8+ installed
- OpenAI API key (required)
- Internet connection for real-time data

## ⚡ Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here
```

### 3. Launch the Application
```bash
# Option 1: Use the launcher script
python run.py

# Option 2: Direct streamlit command
streamlit run app.py
```

### 4. Access the Web Interface
Open your browser to: `http://localhost:8501`

## 🎯 First Steps

### Test the System
1. Go to the **AI Chat** tab
2. Try asking: *"What's your analysis of Apple (AAPL) stock?"*
3. Explore the **Market Data** tab for live charts
4. Browse the **Knowledge Base** for financial concepts

### Example Questions to Try
- *"How should I diversify a $50,000 portfolio?"*
- *"What do the technical indicators show for Tesla?"*
- *"Explain what P/E ratio means and how to use it"*
- *"What's the current market outlook?"*

## 🔧 Troubleshooting

### Common Issues

**"OpenAI API key not configured"**
- Check your `.env` file exists
- Ensure your API key is valid and has billing set up

**"Module not found" errors**
- Run: `pip install -r requirements.txt`
- Make sure you're in the project directory

**Slow responses**
- First-time setup downloads AI models (normal)
- Check your internet connection
- Verify API key has sufficient credits

**No stock data**
- Yahoo Finance API is free but can be rate-limited
- Try again in a few minutes
- Check if the stock symbol is valid

## 🎨 Features Overview

### 💬 AI Chat Assistant
- Ask financial questions in natural language
- Get expert analysis with real-time data
- Conversational memory for context

### 📈 Market Data Dashboard
- Live stock prices and charts
- Technical indicators (RSI, Moving Averages)
- Sector performance analysis

### 📚 Knowledge Base
- Financial concepts and definitions
- Search for specific topics
- Browse by category

### ⚙️ System Status
- Check API connectivity
- Monitor system health
- View configuration

## 🔑 Getting API Keys

### OpenAI API Key (Required)
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create account and verify email
3. Go to API Keys section
4. Click "Create new secret key"
5. Copy and paste into `.env` file
6. Add billing information for usage

### Alpha Vantage (Optional)
1. Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Sign up for free account
3. Get API key from dashboard
4. Add to `.env` file for enhanced economic data

## 📱 Usage Examples

### Stock Analysis
```
User: "Analyze Microsoft stock for me"
AI: Provides comprehensive analysis including:
- Current price and performance
- Financial metrics (P/E, Market Cap)
- Technical indicators
- Risk assessment
- Investment recommendation
```

### Portfolio Advice
```
User: "I'm 25 with $30k to invest. What should I do?"
AI: Offers personalized advice considering:
- Age and risk tolerance
- Diversification strategies
- Asset allocation recommendations
- Time horizon considerations
```

### Market Insights
```
User: "What's happening in the market today?"
AI: Provides market overview including:
- Major index performance
- Sector winners/losers
- Economic factors
- Trading volume analysis
```

## 🛡️ Important Reminders

- **Educational Use**: This system is for learning and information only
- **Not Financial Advice**: Always consult qualified professionals
- **Risk Warning**: All investments carry risk of loss
- **Data Accuracy**: Market data is real-time but verify important decisions

## 🆘 Need Help?

1. **Check the main README.md** for detailed documentation
2. **Run tests**: `python examples/example_queries.py`
3. **System status**: Check the "About" tab in the web interface
4. **Common issues**: See troubleshooting section above

## 🎉 You're Ready!

Your Financial AI Agent is now running! Start by asking it financial questions and exploring the market data features.

**Happy investing! 📈**

---

*Remember: This tool enhances your financial knowledge but should never replace professional financial advice.*