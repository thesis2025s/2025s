#!/usr/bin/env python3
"""
Finance Specialist AI - Application Launcher
Run this script to start the Finance Specialist AI system.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_environment():
    """Check if the environment is properly configured."""
    logger.info("Checking environment configuration...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        logger.warning(".env file not found. Creating from template...")
        env_example = Path(".env.example")
        if env_example.exists():
            import shutil
            shutil.copy(".env.example", ".env")
            logger.info("Created .env file from template. Please configure your API keys.")
        else:
            logger.error(".env.example file not found!")
            return False
    
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    from dotenv import load_dotenv
    load_dotenv()
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please configure your .env file with the required API keys.")
        return False
    
    logger.info("Environment configuration check passed!")
    return True


def install_dependencies():
    """Install required dependencies."""
    logger.info("Checking dependencies...")
    
    try:
        # Try importing key packages
        import streamlit
        import langchain
        import openai
        logger.info("Dependencies check passed!")
        return True
    except ImportError as e:
        logger.warning(f"Missing dependencies: {e}")
        logger.info("Installing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            logger.info("Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False


def create_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "logs", 
        "data/chroma",
        "data/uploads",
        "data/exports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def run_streamlit():
    """Run the Streamlit application."""
    logger.info("Starting Finance Specialist AI...")
    
    # Set Streamlit configuration
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
    os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
    
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ]
        
        logger.info("Streamlit command: " + " ".join(cmd))
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application stopped by user.")
        sys.exit(0)


def main():
    """Main function to run the application."""
    print("🚀 Finance Specialist AI - Starting Up...")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed!")
        print("Please configure your .env file and try again.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed!")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    print("\n✅ All checks passed! Starting the application...")
    print("\n🌐 The application will be available at: http://localhost:8501")
    print("💡 Press Ctrl+C to stop the application")
    print("=" * 50)
    
    # Run the application
    run_streamlit()


if __name__ == "__main__":
    main()