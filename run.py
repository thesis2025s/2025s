#!/usr/bin/env python3
"""
Financial AI Agent Launcher
Simple script to start the Streamlit application
"""
import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if requirements are installed"""
    try:
        import streamlit
        import openai
        import langchain
        import yfinance
        import chromadb
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️ .env file not found")
        print("Please copy .env.example to .env and add your API keys")
        return False
    
    # Read .env file and check for required keys
    with open(env_file) as f:
        content = f.read()
    
    if "OPENAI_API_KEY=" in content and "your_openai_api_key_here" not in content:
        print("✅ OpenAI API key configured")
        return True
    else:
        print("⚠️ OpenAI API key not configured in .env file")
        print("Please add your OpenAI API key to the .env file")
        return False

def run_streamlit():
    """Launch the Streamlit application"""
    try:
        print("🚀 Starting Financial AI Agent...")
        print("📊 Web interface will open at: http://localhost:8501")
        print("🛑 Press Ctrl+C to stop the application\n")
        
        # Run streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main launcher function"""
    print("📈 Financial AI Agent Launcher")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment configuration
    if not check_env_file():
        print("\n💡 Quick setup:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenAI API key")
        print("3. Run this script again")
        sys.exit(1)
    
    # Launch the application
    run_streamlit()

if __name__ == "__main__":
    main()