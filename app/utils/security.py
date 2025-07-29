"""
Security utilities for Finance Specialist AI.
Includes rate limiting, input validation, and security checks.
"""

import re
import hashlib
import hmac
import time
import logging
from typing import Dict, Any, Optional, List
from functools import wraps
from datetime import datetime, timedelta
import streamlit as st

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls and user requests."""
    
    def __init__(self):
        self.requests = {}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def is_allowed(self, identifier: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        """Check if request is allowed based on rate limits."""
        now = time.time()
        
        # Cleanup old entries periodically
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries()
            self.last_cleanup = now
        
        # Get or create request history for identifier
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        request_times = self.requests[identifier]
        
        # Remove requests outside the window
        cutoff_time = now - window_seconds
        request_times[:] = [t for t in request_times if t > cutoff_time]
        
        # Check if under limit
        if len(request_times) < max_requests:
            request_times.append(now)
            return True
        
        return False
    
    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory bloat."""
        cutoff_time = time.time() - 3600  # 1 hour
        
        for identifier in list(self.requests.keys()):
            request_times = self.requests[identifier]
            request_times[:] = [t for t in request_times if t > cutoff_time]
            
            # Remove empty entries
            if not request_times:
                del self.requests[identifier]


class InputValidator:
    """Validates and sanitizes user inputs."""
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 5000) -> str:
        """Sanitize text input."""
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove potential script tags and other dangerous content
        text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        
        # Clean up excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def validate_stock_symbol(symbol: str) -> bool:
        """Validate stock symbol format."""
        if not isinstance(symbol, str):
            return False
        
        # Basic symbol validation (alphanumeric, 1-5 characters)
        pattern = r'^[A-Z]{1,5}$'
        return bool(re.match(pattern, symbol.upper()))
    
    @staticmethod
    def validate_amount(amount: Any) -> bool:
        """Validate monetary amounts."""
        try:
            float_amount = float(amount)
            return 0 <= float_amount <= 1_000_000_000  # Max 1 billion
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Check if filename is safe for upload."""
        if not isinstance(filename, str):
            return False
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'\.\./',  # Path traversal
            r'[<>:"|?*]',  # Invalid filename characters
            r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$',  # Windows reserved names
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return False
        
        # Check file extension
        safe_extensions = {'.txt', '.csv', '.xlsx', '.pdf', '.json'}
        file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        return file_ext in safe_extensions


class SecurityManager:
    """Main security manager for the application."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.validator = InputValidator()
        self.session_tokens = {}
    
    def check_rate_limit(self, session_id: str, action: str = "general") -> bool:
        """Check rate limits for user actions."""
        # Different limits for different actions
        limits = {
            "general": (20, 60),      # 20 requests per minute
            "query": (10, 60),        # 10 queries per minute
            "upload": (5, 300),       # 5 uploads per 5 minutes
            "export": (3, 300),       # 3 exports per 5 minutes
        }
        
        max_requests, window = limits.get(action, limits["general"])
        identifier = f"{session_id}:{action}"
        
        return self.rate_limiter.is_allowed(identifier, max_requests, window)
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate user query for security and content."""
        result = {
            "is_valid": True,
            "sanitized_query": "",
            "warnings": [],
            "blocked_reasons": []
        }
        
        try:
            # Check length
            if len(query) > 5000:
                result["blocked_reasons"].append("Query too long (max 5000 characters)")
                result["is_valid"] = False
                return result
            
            # Sanitize content
            sanitized = self.validator.sanitize_text(query)
            result["sanitized_query"] = sanitized
            
            # Check for potential injection attempts
            suspicious_patterns = [
                r'<script',
                r'javascript:',
                r'eval\(',
                r'exec\(',
                r'__import__',
                r'subprocess',
                r'os\.system',
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    result["warnings"].append(f"Suspicious pattern detected: {pattern}")
            
            # Check for excessive repeated characters (potential spam)
            if re.search(r'(.)\1{50,}', query):
                result["warnings"].append("Excessive character repetition detected")
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating query: {e}")
            result["is_valid"] = False
            result["blocked_reasons"].append("Validation error")
            return result
    
    def generate_session_token(self, session_id: str) -> str:
        """Generate a secure session token."""
        timestamp = str(int(time.time()))
        data = f"{session_id}:{timestamp}"
        
        # In production, use a proper secret key
        secret_key = "finance_ai_secret_key_change_in_production"
        
        token = hmac.new(
            secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        self.session_tokens[session_id] = {
            "token": token,
            "timestamp": timestamp,
            "created": datetime.now()
        }
        
        return token
    
    def verify_session_token(self, session_id: str, token: str) -> bool:
        """Verify a session token."""
        try:
            stored_data = self.session_tokens.get(session_id)
            if not stored_data:
                return False
            
            # Check if token is expired (24 hours)
            created = stored_data["created"]
            if datetime.now() - created > timedelta(hours=24):
                del self.session_tokens[session_id]
                return False
            
            return stored_data["token"] == token
            
        except Exception as e:
            logger.error(f"Error verifying session token: {e}")
            return False
    
    def log_security_event(self, event_type: str, session_id: str, details: Dict[str, Any]):
        """Log security-related events."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "session_id": session_id,
            "details": details
        }
        
        logger.warning(f"Security Event: {log_entry}")


# Global security manager instance
security_manager = SecurityManager()


def rate_limit(action: str = "general"):
    """Decorator for rate limiting."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session_id = getattr(st.session_state, 'session_id', 'unknown')
            
            if not security_manager.check_rate_limit(session_id, action):
                st.error(f"Rate limit exceeded for {action}. Please wait before trying again.")
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_input(input_type: str = "text"):
    """Decorator for input validation."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add input validation logic based on input_type
            return func(*args, **kwargs)
        return wrapper
    return decorator