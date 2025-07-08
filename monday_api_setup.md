# Monday.com API Setup Guide

## Overview
This guide explains how to obtain and configure your Monday.com API key to use the board reader script and access Monday.com data programmatically.

## Getting Your Monday.com API Key

### Method 1: Personal API Token (Recommended for Development)

1. **Log into Monday.com**
   - Go to https://automwrite.monday.com
   - Log in with your credentials

2. **Navigate to Developer Section**
   - Click your profile picture in the top right corner
   - Select "Admin" from the dropdown menu
   - Go to "API" section in the left sidebar

3. **Generate API Token**
   - Click "Generate Token"
   - Give your token a descriptive name (e.g., "Automwrite Agent API")
   - Select the appropriate scopes (permissions):
     - `boards:read` - Read board data
     - `boards:write` - Create/update board items
     - `users:read` - Read user information
     - `account:read` - Read account information
     - `workspaces:read` - Read workspace information

4. **Copy Your Token**
   - Copy the generated token immediately
   - Store it securely (you won't be able to see it again)

### Method 2: OAuth App (For Production Use)

1. **Create a Monday App**
   - Go to https://monday.com/developers/apps
   - Click "Create App"
   - Fill in app details:
     - Name: "Automwrite Agent"
     - Description: "Agent for managing Monday.com boards"
     - Category: "Productivity"

2. **Configure OAuth Settings**
   - Add OAuth scopes needed
   - Set redirect URL (for web-based authentication)
   - Get Client ID and Client Secret

## Environment Setup

### Option 1: Environment Variables (Recommended)

Create a `.env` file in your project root:

```bash
# .env file
MONDAY_API_KEY=your_monday_api_key_here
MONDAY_DOMAIN=https://automwrite.monday.com
```

Load environment variables in your Python script:

```python
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MONDAY_API_KEY")
domain = os.getenv("MONDAY_DOMAIN")
```

### Option 2: Export Environment Variables

```bash
export MONDAY_API_KEY="your_monday_api_key_here"
export MONDAY_DOMAIN="https://automwrite.monday.com"
```

### Option 3: Direct Configuration (Not Recommended for Production)

```python
# Only for testing - don't commit API keys to version control
API_KEY = "your_monday_api_key_here"
```

## Using the Monday Boards Reader Script

### 1. Install Dependencies

```bash
pip install requests python-dotenv
```

### 2. Configure API Key

Set your API key using one of the methods above.

### 3. Run the Script

```bash
python monday_boards_reader.py
```

### 4. Script Output

The script will:
- Connect to your Monday.com account
- Fetch all boards, workspaces, and users
- Export data to `monday_boards_data.json`
- Print summary information

Expected output:
```
INFO:__main__:Starting Monday.com data export...
INFO:__main__:Fetching account information...
INFO:__main__:Fetching workspaces...
INFO:__main__:Fetching users...
INFO:__main__:Fetching all boards...
INFO:__main__:Fetched 25 boards from page 1
INFO:__main__:Successfully exported 25 boards to monday_boards_data.json
Successfully exported Monday.com data!
Found 25 boards
Found 3 workspaces
Found 8 users
```

## Customizing the Script

### Filtering Specific Boards

```python
# Get only specific boards
def get_specific_boards(self, board_ids: List[str]) -> List[Dict]:
    query = """
    query ($board_ids: [ID!]) {
        boards(ids: $board_ids) {
            id
            name
            description
            items {
                id
                name
                column_values {
                    id
                    title
                    text
                    value
                }
            }
        }
    }
    """
    variables = {"board_ids": board_ids}
    response = self._make_request(query, variables)
    return response.get("data", {}).get("boards", [])
```

### Filtering by Date Range

```python
# Get items updated in the last 30 days
def get_recent_items(self, board_id: str, days: int = 30) -> List[Dict]:
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    cutoff_iso = cutoff_date.isoformat()
    
    query = """
    query ($board_id: ID!, $since: Date) {
        boards(ids: [$board_id]) {
            items(since: $since) {
                id
                name
                updated_at
                column_values {
                    id
                    title
                    text
                    value
                }
            }
        }
    }
    """
    variables = {"board_id": board_id, "since": cutoff_iso}
    response = self._make_request(query, variables)
    return response.get("data", {}).get("boards", [{}])[0].get("items", [])
```

## API Rate Limits and Best Practices

### Rate Limits
- **Complexity Limit**: 10M complexity points per month
- **Rate Limit**: 60 requests per minute per user
- **Concurrent Requests**: Maximum 5 concurrent requests

### Best Practices

1. **Implement Caching**
   ```python
   import time
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def cached_board_data(board_id: str, ttl_hash: str = None):
       # TTL hash changes every hour to invalidate cache
       return self.get_board_data(board_id)
   
   # Usage
   ttl_hash = str(int(time.time()) // 3600)  # Changes every hour
   data = cached_board_data(board_id, ttl_hash)
   ```

2. **Implement Rate Limiting**
   ```python
   import time
   from datetime import datetime, timedelta
   
   class RateLimiter:
       def __init__(self, max_requests=50, time_window=60):
           self.max_requests = max_requests
           self.time_window = time_window
           self.requests = []
       
       def wait_if_needed(self):
           now = datetime.now()
           # Remove old requests
           self.requests = [req for req in self.requests 
                           if now - req < timedelta(seconds=self.time_window)]
           
           if len(self.requests) >= self.max_requests:
               sleep_time = self.time_window - (now - self.requests[0]).total_seconds()
               if sleep_time > 0:
                   time.sleep(sleep_time)
           
           self.requests.append(now)
   ```

3. **Error Handling and Retries**
   ```python
   import time
   from requests.exceptions import RequestException
   
   def make_request_with_retry(self, query, variables=None, max_retries=3):
       for attempt in range(max_retries):
           try:
               return self._make_request(query, variables)
           except RequestException as e:
               if attempt == max_retries - 1:
                   raise
               wait_time = 2 ** attempt  # Exponential backoff
               time.sleep(wait_time)
   ```

## Security Considerations

### API Key Storage
- **Never commit API keys to version control**
- **Use environment variables or secure vaults**
- **Rotate API keys regularly**
- **Use least privilege principle for scopes**

### Data Protection
- **Encrypt sensitive data at rest**
- **Use HTTPS for all API communications**
- **Implement proper access controls**
- **Audit API usage regularly**

## Testing Your Setup

### Quick Test Script

```python
#!/usr/bin/env python3
"""
Quick test script to verify Monday.com API connection
"""

import os
import requests

def test_monday_connection():
    api_key = os.getenv("MONDAY_API_KEY")
    if not api_key:
        print("❌ MONDAY_API_KEY environment variable not set")
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    query = """
    query {
        me {
            id
            name
            email
        }
    }
    """
    
    try:
        response = requests.post(
            "https://api.monday.com/v2",
            json={"query": query},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            print(f"❌ API Error: {data['errors']}")
            return False
        
        user_info = data.get("data", {}).get("me", {})
        print(f"✅ Connected successfully as: {user_info.get('name')} ({user_info.get('email')})")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_monday_connection()
```

## Troubleshooting Common Issues

### Issue: "Invalid API Token"
**Solution**: 
- Verify the API key is correct
- Check if the token has expired
- Ensure proper scopes are granted

### Issue: "Rate Limit Exceeded"
**Solution**:
- Implement rate limiting in your code
- Reduce request frequency
- Use caching to minimize API calls

### Issue: "Board Not Found"
**Solution**:
- Verify board ID is correct
- Check if you have permissions to access the board
- Ensure the board hasn't been deleted

### Issue: "GraphQL Syntax Error"
**Solution**:
- Validate your GraphQL query syntax
- Test queries in Monday.com's GraphQL playground
- Check for required variables

## Next Steps

1. **Set up your API key** using one of the methods above
2. **Test the connection** with the quick test script
3. **Run the full board reader script** to export your data
4. **Review the exported data** in `monday_boards_data.json`
5. **Customize the script** for your specific needs

For more advanced usage, refer to the [Monday.com API documentation](https://developer.monday.com/api-reference/) and the comprehensive README file.