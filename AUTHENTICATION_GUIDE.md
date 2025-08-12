# NBA API Authentication Guide

This guide explains how to set up authentication for the NBA API infrastructure.

## Overview

The NBA.com API has various authentication methods and strict rate limiting. This infrastructure supports multiple authentication approaches to maximize data access.

## Authentication Methods

### 1. Browser-like Headers (Default)

**Best for:** Most use cases, basic data access
**Requirements:** None
**Success Rate:** Medium (may be blocked by rate limiting)

This method uses browser-like headers to mimic legitimate web traffic:

```python
from nba.sources.nba_client import NBAAPIClient

# Uses browser-like headers by default
client = NBAAPIClient()
teams = client.get_teams()
```

### 2. API Key Authentication

**Best for:** Official API access (if you have an API key)
**Requirements:** NBA API key
**Success Rate:** High (if you have official access)

```bash
# Set in environment
export NBA_API_KEY="your_api_key_here"

# Or in .env file
NBA_API_KEY=your_api_key_here
```

```python
from nba.sources.nba_client import NBAAPIClient

# Will automatically use API key from environment
client = NBAAPIClient()
```

### 3. Session-based Authentication

**Best for:** Web scraping with login
**Requirements:** NBA.com account
**Success Rate:** Medium (may be blocked)

```python
from nba.sources.auth import NBAAPIAuthenticator

authenticator = NBAAPIAuthenticator()
success = authenticator.authenticate_with_session("username", "password")

if success:
    client = NBAAPIClient(authenticator=authenticator)
```

### 4. OAuth Tokens

**Best for:** Third-party integrations
**Requirements:** OAuth tokens
**Success Rate:** High (if tokens are valid)

```bash
# Set in environment
export NBA_ACCESS_TOKEN="your_access_token"
export NBA_REFRESH_TOKEN="your_refresh_token"
```

## Quick Setup

### Option 1: Interactive Setup

Run the interactive setup script:

```bash
python setup_auth.py
```

This will guide you through the authentication setup process.

### Option 2: Manual Setup

1. Copy the environment template:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` with your credentials:
   ```bash
   # Add your NBA API key if you have one
   NBA_API_KEY=your_api_key_here
   ```

3. Test the setup:
   ```bash
   python simple_demo.py
   ```

## Rate Limiting

NBA.com has strict rate limiting. The infrastructure includes built-in rate limiting:

- **Default delay:** 1 second between requests
- **Configurable:** Set `NBA_RATE_LIMIT_DELAY` in environment
- **Automatic retries:** 5 retries with exponential backoff

### Rate Limiting Configuration

```bash
# In .env file
NBA_RATE_LIMIT_DELAY=2.0  # 2 seconds between requests
NBA_MAX_REQUESTS_PER_MINUTE=30  # Conservative limit
```

## Testing Authentication

### Test Basic Setup

```python
from nba.sources.auth import get_authenticator

authenticator = get_authenticator()
if authenticator.test_authentication():
    print("✓ Authentication working!")
else:
    print("⚠ Authentication failed - may be rate limited")
```

### Test API Client

```python
from nba.sources.nba_client import NBAAPIClient

client = NBAAPIClient()

try:
    teams = client.get_teams()
    print(f"✓ Retrieved {len(teams)} teams")
except Exception as e:
    print(f"✗ API call failed: {e}")
```

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   - NBA.com may block automated requests
   - Try increasing delays between requests
   - Use different User-Agent headers

2. **Rate Limiting**
   - Increase `NBA_RATE_LIMIT_DELAY`
   - Reduce `NBA_MAX_REQUESTS_PER_MINUTE`
   - Add random delays between requests

3. **Authentication Failures**
   - Check if credentials are valid
   - Try different authentication methods
   - Verify environment variables are set

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from nba.sources.nba_client import NBAAPIClient
client = NBAAPIClient()
```

## Alternative Data Sources

If NBA.com API access is problematic, consider:

1. **Basketball Reference API** - More reliable, requires subscription
2. **ESPN API** - Limited but accessible
3. **Local data files** - For testing and development
4. **Web scraping** - More complex but flexible

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Rotate API keys** regularly
4. **Monitor API usage** to avoid rate limiting
5. **Use secure credential storage** in production

## Production Deployment

For production use:

1. **Use secure credential storage** (AWS Secrets Manager, etc.)
2. **Implement proper error handling**
3. **Add monitoring and alerting**
4. **Use connection pooling**
5. **Implement circuit breakers** for API failures

## Example Usage

```python
from nba.sources.nba_client import NBAAPIClient
from nba.ingest import ingest_teams, ingest_games

# Create authenticated client
client = NBAAPIClient()

# Ingest data
teams = ingest_teams()
games = ingest_games(2023, "Regular Season")

print(f"✓ Ingested {len(teams)} teams and {len(games)} games")
```

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review NBA.com's terms of service
3. Consider using alternative data sources
4. Contact the development team for assistance

---

**Note:** NBA.com's API access and rate limiting policies may change. This guide will be updated as needed.
