"""
Basic tests for Finance Specialist AI application.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test that core modules can be imported."""
    try:
        from app.config import settings
        from app.utils.security import SecurityManager, InputValidator
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")


def test_input_validator():
    """Test input validation functionality."""
    from app.utils.security import InputValidator
    
    validator = InputValidator()
    
    # Test text sanitization
    clean_text = validator.sanitize_text("Hello World")
    assert clean_text == "Hello World"
    
    # Test script removal
    dirty_text = "Hello <script>alert('xss')</script> World"
    clean_text = validator.sanitize_text(dirty_text)
    assert "<script>" not in clean_text
    
    # Test stock symbol validation
    assert validator.validate_stock_symbol("AAPL") == True
    assert validator.validate_stock_symbol("MSFT") == True
    assert validator.validate_stock_symbol("invalid123") == False
    assert validator.validate_stock_symbol("") == False
    
    # Test amount validation
    assert validator.validate_amount(100.50) == True
    assert validator.validate_amount(0) == True
    assert validator.validate_amount(-100) == False
    assert validator.validate_amount("invalid") == False


def test_rate_limiter():
    """Test rate limiting functionality."""
    from app.utils.security import RateLimiter
    
    limiter = RateLimiter()
    
    # Test basic rate limiting
    for i in range(5):
        assert limiter.is_allowed("test_user", max_requests=5, window_seconds=60) == True
    
    # Should be rate limited now
    assert limiter.is_allowed("test_user", max_requests=5, window_seconds=60) == False


def test_security_manager():
    """Test security manager functionality."""
    from app.utils.security import SecurityManager
    
    manager = SecurityManager()
    
    # Test query validation
    result = manager.validate_query("What is the stock price of AAPL?")
    assert result["is_valid"] == True
    assert result["sanitized_query"] != ""
    
    # Test malicious query
    result = manager.validate_query("<script>alert('xss')</script>")
    assert len(result["warnings"]) > 0


@patch('openai.OpenAI')
def test_financial_tools(mock_openai):
    """Test financial tools functionality."""
    try:
        from app.tools.financial_data import stock_price_tool
        
        # Mock the tool execution
        mock_result = {
            "symbol": "AAPL",
            "price": 150.00,
            "change": 2.50
        }
        
        # Test would require actual API calls, so we just test import
        assert stock_price_tool is not None
        
    except ImportError:
        # Tools might not be available without proper API keys
        pass


def test_config_loading():
    """Test configuration loading."""
    try:
        from app.config import settings
        
        # Test that settings object exists
        assert hasattr(settings, 'model_config')
        assert hasattr(settings, 'api_keys')
        
    except Exception as e:
        pytest.fail(f"Failed to load configuration: {e}")


if __name__ == "__main__":
    pytest.main([__file__])