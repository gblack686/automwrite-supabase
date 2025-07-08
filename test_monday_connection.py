#!/usr/bin/env python3
"""
Quick test script to verify Monday.com API connection
"""

import os
import requests
import json
from datetime import datetime


def test_monday_connection():
    """Test basic connection to Monday.com API"""
    api_key = os.getenv("MONDAY_API_KEY")
    if not api_key:
        print("❌ MONDAY_API_KEY environment variable not set")
        print("Please set your Monday.com API key:")
        print("export MONDAY_API_KEY='your_api_key_here'")
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
            account {
                id
                name
                slug
            }
        }
    }
    """
    
    try:
        print("🔄 Testing Monday.com API connection...")
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
        account_info = user_info.get("account", {})
        
        print("✅ Connected successfully!")
        print(f"   User: {user_info.get('name')} ({user_info.get('email')})")
        print(f"   Account: {account_info.get('name')} ({account_info.get('slug')})")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_boards_access():
    """Test access to boards"""
    api_key = os.getenv("MONDAY_API_KEY")
    if not api_key:
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    query = """
    query {
        boards(limit: 5) {
            id
            name
            description
            type
            state
            items_count
            workspace {
                id
                name
            }
        }
    }
    """
    
    try:
        print("\n🔄 Testing boards access...")
        response = requests.post(
            "https://api.monday.com/v2",
            json={"query": query},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            print(f"❌ Boards API Error: {data['errors']}")
            return False
        
        boards = data.get("data", {}).get("boards", [])
        print(f"✅ Successfully accessed {len(boards)} boards")
        
        for board in boards:
            workspace = board.get("workspace", {})
            print(f"   📋 {board.get('name')} (ID: {board.get('id')})")
            print(f"      Workspace: {workspace.get('name', 'N/A')}")
            print(f"      Items: {board.get('items_count', 0)}")
            print(f"      Type: {board.get('type', 'N/A')}")
            print(f"      State: {board.get('state', 'N/A')}")
            print()
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Boards access failed: {e}")
        return False


def run_full_test():
    """Run comprehensive API test"""
    print("🚀 Starting Monday.com API Connection Test")
    print("=" * 50)
    
    # Test basic connection
    if not test_monday_connection():
        print("\n❌ Basic connection test failed. Please check your API key.")
        return False
    
    # Test boards access
    if not test_boards_access():
        print("\n❌ Boards access test failed. Please check your permissions.")
        return False
    
    print("\n✅ All tests passed! Your Monday.com API is working correctly.")
    print("\nNext steps:")
    print("1. Run: python monday_boards_reader.py")
    print("2. Check the generated monday_boards_data.json file")
    print("3. Review the comprehensive README file")
    
    return True


if __name__ == "__main__":
    run_full_test()