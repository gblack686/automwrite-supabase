#!/usr/bin/env python3
"""
SmartLead API Data Fetcher and README Updater

This script connects to the SmartLead API to fetch current data about campaigns,
leads, email accounts, and other essential elements. It then updates the README
file with fresh information for Automwrite agents to reference.

Requirements:
- requests library
- python-dotenv (optional, for environment variables)
- SmartLead API key

Usage:
    python update_readme.py

Environment Variables:
    SMARTLEAD_API_KEY: Your SmartLead API key
    
Author: Automwrite
Date: January 2025
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import time

# Try to import dotenv for environment variable management
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Using system environment variables only.")

class SmartLeadAPIClient:
    """SmartLead API client for fetching data and updating documentation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the SmartLead API client.
        
        Args:
            api_key: SmartLead API key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.getenv('SMARTLEAD_API_KEY')
        if not self.api_key:
            raise ValueError("SmartLead API key is required. Set SMARTLEAD_API_KEY environment variable or pass as parameter.")
        
        self.base_url = "https://api.smartlead.ai"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make a request to the SmartLead API with error handling and rate limiting.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: For API errors
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                response = self.session.request(method, url, **kwargs)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def get_campaigns(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch all campaigns from SmartLead.
        
        Args:
            limit: Maximum number of campaigns to fetch
            
        Returns:
            List of campaign dictionaries
        """
        try:
            response = self._make_request('GET', '/campaigns', params={'limit': limit})
            return response.get('data', [])
        except Exception as e:
            print(f"Error fetching campaigns: {e}")
            return []
    
    def get_leads(self, campaign_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch leads from SmartLead.
        
        Args:
            campaign_id: If provided, fetch leads for specific campaign
            limit: Maximum number of leads to fetch
            
        Returns:
            List of lead dictionaries
        """
        try:
            if campaign_id:
                endpoint = f'/campaigns/{campaign_id}/leads'
            else:
                endpoint = '/leads'
            
            response = self._make_request('GET', endpoint, params={'limit': limit})
            return response.get('data', [])
        except Exception as e:
            print(f"Error fetching leads: {e}")
            return []
    
    def get_email_accounts(self) -> List[Dict[str, Any]]:
        """
        Fetch all email accounts from SmartLead.
        
        Returns:
            List of email account dictionaries
        """
        try:
            response = self._make_request('GET', '/email-accounts')
            return response.get('data', [])
        except Exception as e:
            print(f"Error fetching email accounts: {e}")
            return []
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """
        Fetch statistics for a specific campaign.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Campaign statistics dictionary
        """
        try:
            response = self._make_request('GET', f'/campaigns/{campaign_id}/stats')
            return response.get('data', {})
        except Exception as e:
            print(f"Error fetching campaign stats for {campaign_id}: {e}")
            return {}
    
    def get_global_analytics(self) -> Dict[str, Any]:
        """
        Fetch global account analytics.
        
        Returns:
            Global analytics dictionary
        """
        try:
            response = self._make_request('GET', '/analytics/overall')
            return response.get('data', {})
        except Exception as e:
            print(f"Error fetching global analytics: {e}")
            return {}
    
    def get_lead_categories(self) -> List[Dict[str, Any]]:
        """
        Fetch available lead categories/statuses.
        
        Returns:
            List of lead category dictionaries
        """
        try:
            response = self._make_request('GET', '/leads/categories')
            return response.get('data', [])
        except Exception as e:
            print(f"Error fetching lead categories: {e}")
            return []

class SmartLeadDataAnalyzer:
    """Analyze SmartLead data and generate insights for README updates."""
    
    def __init__(self, client: SmartLeadAPIClient):
        """
        Initialize the data analyzer.
        
        Args:
            client: SmartLead API client instance
        """
        self.client = client
        
    def analyze_account_overview(self) -> Dict[str, Any]:
        """
        Generate an overview of the SmartLead account.
        
        Returns:
            Account overview dictionary
        """
        print("Analyzing account overview...")
        
        campaigns = self.client.get_campaigns()
        email_accounts = self.client.get_email_accounts()
        global_analytics = self.client.get_global_analytics()
        lead_categories = self.client.get_lead_categories()
        
        # Sample leads from first campaign if available
        sample_leads = []
        if campaigns:
            sample_leads = self.client.get_leads(campaigns[0].get('id'), limit=10)
        
        overview = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_campaigns': len(campaigns),
            'total_email_accounts': len(email_accounts),
            'active_campaigns': len([c for c in campaigns if c.get('status') == 'active']),
            'campaign_statuses': self._get_status_distribution(campaigns, 'status'),
            'email_account_statuses': self._get_status_distribution(email_accounts, 'status'),
            'lead_categories': [cat.get('name', 'Unknown') for cat in lead_categories],
            'sample_campaign_names': [c.get('name', 'Unnamed') for c in campaigns[:5]],
            'global_analytics': global_analytics,
            'sample_leads_count': len(sample_leads)
        }
        
        return overview
    
    def _get_status_distribution(self, items: List[Dict], status_field: str) -> Dict[str, int]:
        """
        Get distribution of statuses in a list of items.
        
        Args:
            items: List of items with status field
            status_field: Name of the status field
            
        Returns:
            Dictionary with status counts
        """
        distribution = {}
        for item in items:
            status = item.get(status_field, 'unknown')
            distribution[status] = distribution.get(status, 0) + 1
        return distribution
    
    def generate_campaign_insights(self) -> Dict[str, Any]:
        """
        Generate insights about campaigns.
        
        Returns:
            Campaign insights dictionary
        """
        print("Generating campaign insights...")
        
        campaigns = self.client.get_campaigns()
        insights = {
            'total_campaigns': len(campaigns),
            'campaign_types': {},
            'recent_campaigns': [],
            'performance_summary': {}
        }
        
        # Analyze campaign performance for active campaigns
        active_campaigns = [c for c in campaigns if c.get('status') == 'active']
        for campaign in active_campaigns[:3]:  # Limit to avoid rate limits
            campaign_id = campaign.get('id')
            if campaign_id:
                stats = self.client.get_campaign_stats(str(campaign_id))
                if stats:
                    insights['performance_summary'][campaign.get('name', f'Campaign {campaign_id}')] = {
                        'opens': stats.get('opens', 0),
                        'replies': stats.get('replies', 0),
                        'bounces': stats.get('bounces', 0)
                    }
        
        return insights

class READMEUpdater:
    """Update README file with fresh SmartLead data."""
    
    def __init__(self, readme_path: str = 'smartlead_api_readme.md'):
        """
        Initialize the README updater.
        
        Args:
            readme_path: Path to the README file
        """
        self.readme_path = readme_path
        
    def update_readme_with_data(self, overview: Dict[str, Any], insights: Dict[str, Any]):
        """
        Update the README file with fresh data.
        
        Args:
            overview: Account overview data
            insights: Campaign insights data
        """
        print(f"Updating README file: {self.readme_path}")
        
        # Read current README
        try:
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"README file not found: {self.readme_path}")
            return False
        
        # Generate data section
        data_section = self._generate_data_section(overview, insights)
        
        # Find insertion point or append to end
        insertion_marker = "## Current Account Status"
        if insertion_marker in content:
            # Replace existing section
            parts = content.split(insertion_marker)
            if len(parts) > 1:
                # Find the next section or end of file
                remaining = parts[1]
                next_section_start = remaining.find('\n## ')
                if next_section_start != -1:
                    content = parts[0] + insertion_marker + data_section + remaining[next_section_start:]
                else:
                    content = parts[0] + insertion_marker + data_section
            else:
                content += f"\n\n{insertion_marker}\n{data_section}"
        else:
            # Add new section before the last line
            content += f"\n\n{insertion_marker}\n{data_section}"
        
        # Write updated README
        try:
            with open(self.readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("README updated successfully!")
            return True
        except Exception as e:
            print(f"Error writing README file: {e}")
            return False
    
    def _generate_data_section(self, overview: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """
        Generate the data section for the README.
        
        Args:
            overview: Account overview data
            insights: Campaign insights data
            
        Returns:
            Formatted data section string
        """
        timestamp = overview.get('timestamp', datetime.now(timezone.utc).isoformat())
        
        section = f"""

*Last Updated: {timestamp}*

### Account Overview
- **Total Campaigns**: {overview.get('total_campaigns', 'N/A')}
- **Active Campaigns**: {overview.get('active_campaigns', 'N/A')}
- **Total Email Accounts**: {overview.get('total_email_accounts', 'N/A')}
- **Sample Leads Analyzed**: {overview.get('sample_leads_count', 'N/A')}

### Campaign Status Distribution
"""
        
        # Add campaign status distribution
        status_dist = overview.get('campaign_statuses', {})
        for status, count in status_dist.items():
            section += f"- **{status.title()}**: {count} campaigns\n"
        
        section += "\n### Email Account Status Distribution\n"
        
        # Add email account status distribution  
        email_status_dist = overview.get('email_account_statuses', {})
        for status, count in email_status_dist.items():
            section += f"- **{status.title()}**: {count} accounts\n"
        
        # Add lead categories if available
        lead_categories = overview.get('lead_categories', [])
        if lead_categories:
            section += f"\n### Available Lead Categories\n"
            for category in lead_categories:
                section += f"- {category}\n"
        
        # Add sample campaign names
        sample_campaigns = overview.get('sample_campaign_names', [])
        if sample_campaigns:
            section += f"\n### Recent Campaigns\n"
            for campaign in sample_campaigns:
                section += f"- {campaign}\n"
        
        # Add performance summary if available
        performance = insights.get('performance_summary', {})
        if performance:
            section += f"\n### Campaign Performance Summary\n"
            for campaign_name, stats in performance.items():
                section += f"- **{campaign_name}**:\n"
                section += f"  - Opens: {stats.get('opens', 'N/A')}\n"
                section += f"  - Replies: {stats.get('replies', 'N/A')}\n"
                section += f"  - Bounces: {stats.get('bounces', 'N/A')}\n"
        
        # Add global analytics if available
        global_analytics = overview.get('global_analytics', {})
        if global_analytics:
            section += f"\n### Global Analytics\n"
            for key, value in global_analytics.items():
                if isinstance(value, (int, float, str)):
                    section += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        section += f"\n---\n*This data was automatically generated from SmartLead API*\n"
        
        return section

def main():
    """Main function to run the SmartLead data fetcher and README updater."""
    print("SmartLead API Data Fetcher and README Updater")
    print("=" * 50)
    
    try:
        # Initialize API client
        print("Initializing SmartLead API client...")
        client = SmartLeadAPIClient()
        
        # Initialize data analyzer
        print("Initializing data analyzer...")
        analyzer = SmartLeadDataAnalyzer(client)
        
        # Fetch and analyze data
        print("Fetching account overview...")
        overview = analyzer.analyze_account_overview()
        
        print("Generating campaign insights...")
        insights = analyzer.generate_campaign_insights()
        
        # Update README
        print("Updating README file...")
        updater = READMEUpdater()
        success = updater.update_readme_with_data(overview, insights)
        
        if success:
            print("\n✅ README updated successfully!")
            print(f"📊 Processed {overview.get('total_campaigns', 0)} campaigns")
            print(f"📧 Analyzed {overview.get('total_email_accounts', 0)} email accounts")
            print(f"📈 Included {len(insights.get('performance_summary', {}))} performance summaries")
        else:
            print("\n❌ Failed to update README")
            sys.exit(1)
            
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("Please set your SMARTLEAD_API_KEY environment variable")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()