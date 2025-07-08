# SmartLead API Tools Setup Guide

This guide helps you set up and use the SmartLead API documentation and update tools for Automwrite agents.

## Files Created

1. **`smartlead_api_readme.md`** - Comprehensive SmartLead API documentation
2. **`update_readme.py`** - Python script to fetch live data and update the README
3. **`requirements.txt`** - Python dependencies for the update script

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `requests` - For making HTTP requests to SmartLead API
- `python-dotenv` - For managing environment variables (optional)

### 2. Configure API Key

You need a SmartLead API key to use the update script.

**Option A: Environment Variable (Recommended)**
```bash
export SMARTLEAD_API_KEY="your_smartlead_api_key_here"
```

**Option B: Create .env file**
```bash
echo "SMARTLEAD_API_KEY=your_smartlead_api_key_here" > .env
```

### 3. Run the Update Script

```bash
python update_readme.py
```

This will:
- Connect to SmartLead API
- Fetch current campaign, lead, and account data
- Update the README with fresh statistics
- Add current account status section

## Usage Examples

### Manual README Updates

```bash
# Run the update script to refresh data
python update_readme.py

# Check the updated README
cat smartlead_api_readme.md
```

### Automated Updates (Cron Job)

To keep the documentation current, set up a cron job:

```bash
# Edit crontab
crontab -e

# Add this line to update every 6 hours
0 */6 * * * cd /path/to/automwrite && python update_readme.py
```

### Integration with Agents

Agents can reference the updated README file to get:
- Current campaign status
- Available email accounts
- Lead categories and statuses
- Recent performance metrics
- Live account statistics

## API Key Security

⚠️ **Important Security Notes:**

1. **Never commit API keys** to version control
2. **Use environment variables** for production
3. **Rotate keys regularly** for security
4. **Limit API key permissions** to only what's needed
5. **Monitor API usage** to detect unauthorized access

## Features

### SmartLead API Client (`update_readme.py`)

- **Authentication**: Secure API key management
- **Rate Limiting**: Automatic handling of API rate limits
- **Error Handling**: Robust error handling with retry logic
- **Data Analysis**: Intelligent parsing of SmartLead data
- **Documentation Updates**: Automatic README updates

### README Documentation (`smartlead_api_readme.md`)

- **Complete API Reference**: All SmartLead endpoints documented
- **Code Examples**: Request/response examples
- **Best Practices**: Security and usage recommendations
- **Live Data Section**: Current account status (updated by script)
- **Common Use Cases**: Practical implementation examples

## Troubleshooting

### Common Issues

**1. "API key is required" Error**
```bash
# Check if API key is set
echo $SMARTLEAD_API_KEY

# If empty, set it
export SMARTLEAD_API_KEY="your_key_here"
```

**2. "Rate limited" Messages**
- The script automatically handles rate limits
- If you see many rate limit messages, reduce the frequency of updates

**3. "README file not found" Error**
```bash
# Ensure you're in the correct directory
ls -la smartlead_api_readme.md

# Run from the directory containing the README
python update_readme.py
```

**4. Import Errors**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or install individually
pip install requests python-dotenv
```

### API Debugging

To debug API issues, modify the script to add more verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Customization

### Adding New Data Points

To fetch additional data from SmartLead API:

1. Add new methods to `SmartLeadAPIClient` class
2. Update `SmartLeadDataAnalyzer` to process the new data
3. Modify `READMEUpdater._generate_data_section()` to include new data

### Changing Update Frequency

Modify the data fetching logic in `analyze_account_overview()`:

```python
# For more frequent updates, increase limits
campaigns = self.client.get_campaigns(limit=200)

# For less frequent updates, decrease limits
campaigns = self.client.get_campaigns(limit=50)
```

### Custom README Sections

To add custom sections to the README:

1. Modify `_generate_data_section()` method
2. Add new analysis methods to `SmartLeadDataAnalyzer`
3. Update the insertion logic in `update_readme_with_data()`

## Integration with Automwrite Agents

### Agent Usage Patterns

1. **Before Campaign Creation**: Check current account status
2. **Performance Monitoring**: Review updated metrics
3. **Lead Management**: Reference current lead categories
4. **Account Health**: Monitor email account status

### Recommended Agent Workflows

```python
# Example agent integration
def get_smartlead_status():
    """Agent function to get current SmartLead status"""
    with open('smartlead_api_readme.md', 'r') as f:
        readme_content = f.read()
    
    # Parse current status section
    if "## Current Account Status" in readme_content:
        status_section = readme_content.split("## Current Account Status")[1]
        return status_section.split("##")[0]  # Get just the status section
    
    return "Status not available - run update_readme.py"
```

## Support

For issues with:
- **SmartLead API**: Contact SmartLead support
- **This tool**: Review error messages and check configuration
- **Agent integration**: Refer to Automwrite agent documentation

---

*Setup guide created for Automwrite agents*
*Last updated: January 2025*