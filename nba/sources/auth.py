"""
NBA API Authentication

This module provides various authentication methods for NBA API access.
NBA.com uses different authentication approaches depending on the endpoint.
"""

import os
import time
import json
from dataclasses import dataclass
from typing import Dict, Any, Optional
import requests
from pathlib import Path

from nba.config import get_settings


@dataclass
class NBAAPIAuth:
    """NBA API authentication configuration."""
    
    # Basic authentication
    api_key: Optional[str] = None
    
    # Session-based authentication
    session_id: Optional[str] = None
    session_token: Optional[str] = None
    
    # OAuth tokens (if available)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    
    # Browser-like headers for web scraping
    use_browser_headers: bool = True
    
    # Rate limiting
    rate_limit_delay: float = 1.0
    max_requests_per_minute: int = 60
    
    def __post_init__(self) -> None:
        """Initialize authentication from environment variables."""
        if self.api_key is None:
            self.api_key = os.getenv("NBA_API_KEY")
        
        if self.session_id is None:
            self.session_id = os.getenv("NBA_SESSION_ID")
            
        if self.session_token is None:
            self.session_token = os.getenv("NBA_SESSION_TOKEN")
            
        if self.access_token is None:
            self.access_token = os.getenv("NBA_ACCESS_TOKEN")


class NBAAPIAuthenticator:
    """Handles NBA API authentication and session management."""
    
    def __init__(self, auth_config: Optional[NBAAPIAuth] = None):
        self.auth = auth_config or NBAAPIAuth()
        self.session = requests.Session()
        self.last_request_time = 0.0
        
        # Set up session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self) -> None:
        """Set up browser-like headers for NBA API requests."""
        if self.auth.use_browser_headers:
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://www.nba.com/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            })
        
        # Add authentication headers if available
        if self.auth.api_key:
            self.session.headers["X-API-Key"] = self.auth.api_key
            
        if self.auth.access_token:
            self.session.headers["Authorization"] = f"Bearer {self.auth.access_token}"
    
    def _rate_limit(self) -> None:
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.auth.rate_limit_delay:
            sleep_time = self.auth.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def authenticate_with_session(self, username: str, password: str) -> bool:
        """
        Authenticate with NBA.com using username/password.
        Note: This may not work for all endpoints due to NBA.com's security.
        """
        try:
            # NBA.com login endpoint (may change)
            login_url = "https://www.nba.com/login"
            
            login_data = {
                "username": username,
                "password": password,
                "remember": True
            }
            
            response = self.session.post(login_url, data=login_data)
            
            if response.status_code == 200:
                # Extract session cookies
                cookies = response.cookies
                if "sessionid" in cookies:
                    self.auth.session_id = cookies["sessionid"]
                return True
            else:
                print(f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def authenticate_with_api_key(self, api_key: str) -> bool:
        """Set up API key authentication."""
        try:
            self.auth.api_key = api_key
            self.session.headers["X-API-Key"] = api_key
            return True
        except Exception as e:
            print(f"API key authentication error: {e}")
            return False
    
    def get_authenticated_headers(self) -> Dict[str, str]:
        """Get headers with current authentication."""
        headers = self.session.headers.copy()
        
        # Add any additional authentication headers
        if self.auth.session_token:
            headers["X-Session-Token"] = self.auth.session_token
            
        return headers
    
    def test_authentication(self) -> bool:
        """Test if current authentication is working."""
        try:
            # Try a simple API call that should work with basic headers
            test_url = "https://stats.nba.com/stats/commonteamroster"
            params = {
                "LeagueID": "00",
                "Season": "2023-24",
                "IsOnlyCurrentSeason": "1"
            }
            
            self._rate_limit()
            response = self.session.get(test_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return "resultSets" in data
            else:
                print(f"Authentication test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Authentication test error: {e}")
            return False
    
    def save_credentials(self, filepath: str = ".nba_credentials") -> None:
        """Save authentication credentials to file (encrypted in production)."""
        credentials = {
            "api_key": self.auth.api_key,
            "session_id": self.auth.session_id,
            "session_token": self.auth.session_token,
            "access_token": self.auth.access_token,
            "refresh_token": self.auth.refresh_token
        }
        
        # Remove None values
        credentials = {k: v for k, v in credentials.items() if v is not None}
        
        with open(filepath, 'w') as f:
            json.dump(credentials, f, indent=2)
        
        print(f"Credentials saved to {filepath}")
    
    def load_credentials(self, filepath: str = ".nba_credentials") -> bool:
        """Load authentication credentials from file."""
        try:
            if not Path(filepath).exists():
                return False
                
            with open(filepath, 'r') as f:
                credentials = json.load(f)
            
            # Update auth config
            for key, value in credentials.items():
                if hasattr(self.auth, key):
                    setattr(self.auth, key, value)
            
            # Update session headers
            self._setup_session_headers()
            
            print(f"Credentials loaded from {filepath}")
            return True
            
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return False


def get_authenticator() -> NBAAPIAuthenticator:
    """Get a configured NBA API authenticator."""
    auth_config = NBAAPIAuth()
    authenticator = NBAAPIAuthenticator(auth_config)
    
    # Try to load saved credentials
    authenticator.load_credentials()
    
    return authenticator


def setup_authentication_interactive() -> NBAAPIAuthenticator:
    """Interactive setup for NBA API authentication."""
    print("🏀 NBA API Authentication Setup")
    print("=" * 40)
    
    authenticator = NBAAPIAuthenticator()
    
    print("\nAvailable authentication methods:")
    print("1. API Key (if you have one)")
    print("2. Session-based authentication")
    print("3. Browser-like headers (default)")
    
    choice = input("\nChoose authentication method (1-3, default 3): ").strip()
    
    if choice == "1":
        api_key = input("Enter your NBA API key: ").strip()
        if api_key:
            if authenticator.authenticate_with_api_key(api_key):
                print("✓ API key authentication set up successfully")
            else:
                print("✗ API key authentication failed")
    
    elif choice == "2":
        username = input("Enter NBA.com username: ").strip()
        password = input("Enter NBA.com password: ").strip()
        if username and password:
            if authenticator.authenticate_with_session(username, password):
                print("✓ Session authentication successful")
            else:
                print("✗ Session authentication failed")
    
    else:
        print("✓ Using browser-like headers (default)")
    
    # Test authentication
    print("\nTesting authentication...")
    if authenticator.test_authentication():
        print("✓ Authentication test passed!")
        
        # Save credentials
        save = input("Save credentials for future use? (y/n): ").strip().lower()
        if save == 'y':
            authenticator.save_credentials()
    else:
        print("⚠ Authentication test failed, but you can still try API calls")
        print("  NBA.com may block automated requests regardless of authentication")
    
    return authenticator
