#!/usr/bin/env python3
"""
Monday.com Boards Reader
This script reads all Monday.com boards and their data using the Monday.com API.
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MondayBoardsReader:
    """Class to read and fetch data from Monday.com boards."""
    
    def __init__(self, api_key: str, domain: str = "https://api.monday.com/v2"):
        """
        Initialize the Monday.com API client.
        
        Args:
            api_key: Your Monday.com API token
            domain: Monday.com API endpoint (default: https://api.monday.com/v2)
        """
        self.api_key = api_key
        self.domain = domain
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "API-Version": "2023-10"
        }
    
    def _make_request(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """
        Make a GraphQL request to Monday.com API.
        
        Args:
            query: GraphQL query string
            variables: Optional variables for the query
            
        Returns:
            JSON response from the API
        """
        data = {"query": query}
        if variables:
            data["variables"] = variables
        
        try:
            response = requests.post(
                self.domain,
                json=data,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_account_info(self) -> Dict:
        """Get account information."""
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
                    plan {
                        max_users
                        period
                        tier
                    }
                }
            }
        }
        """
        return self._make_request(query)
    
    def get_all_boards(self) -> List[Dict]:
        """Get all boards from the account."""
        query = """
        query ($limit: Int, $page: Int) {
            boards (limit: $limit, page: $page) {
                id
                name
                description
                type
                state
                created_at
                updated_at
                board_folder_id
                board_kind
                workspace_id
                workspace {
                    id
                    name
                    description
                }
                owners {
                    id
                    name
                    email
                }
                subscribers {
                    id
                    name
                    email
                }
                tags {
                    id
                    name
                    color
                }
                columns {
                    id
                    title
                    type
                    settings_str
                    archived
                }
                groups {
                    id
                    title
                    color
                    position
                    archived
                }
                items {
                    id
                    name
                    state
                    created_at
                    updated_at
                    creator {
                        id
                        name
                        email
                    }
                    group {
                        id
                        title
                    }
                    column_values {
                        id
                        title
                        type
                        text
                        value
                    }
                    updates {
                        id
                        body
                        created_at
                        creator {
                            id
                            name
                            email
                        }
                    }
                }
            }
        }
        """
        
        all_boards = []
        page = 1
        limit = 25  # Monday.com API limit
        
        while True:
            variables = {"limit": limit, "page": page}
            response = self._make_request(query, variables)
            
            if "errors" in response:
                logger.error(f"API errors: {response['errors']}")
                break
                
            boards = response.get("data", {}).get("boards", [])
            if not boards:
                break
                
            all_boards.extend(boards)
            logger.info(f"Fetched {len(boards)} boards from page {page}")
            
            if len(boards) < limit:
                break
                
            page += 1
        
        return all_boards
    
    def get_workspaces(self) -> List[Dict]:
        """Get all workspaces."""
        query = """
        query {
            workspaces {
                id
                name
                description
                created_at
                owners {
                    id
                    name
                    email
                }
                users {
                    id
                    name
                    email
                }
                teams {
                    id
                    name
                    users {
                        id
                        name
                        email
                    }
                }
            }
        }
        """
        response = self._make_request(query)
        return response.get("data", {}).get("workspaces", [])
    
    def get_users(self) -> List[Dict]:
        """Get all users in the account."""
        query = """
        query {
            users {
                id
                name
                email
                title
                phone
                location
                time_zone
                created_at
                is_admin
                is_guest
                is_pending
                enabled
                account {
                    id
                    name
                }
                teams {
                    id
                    name
                }
            }
        }
        """
        response = self._make_request(query)
        return response.get("data", {}).get("users", [])
    
    def export_all_data(self, output_file: str = "monday_boards_data.json") -> Dict:
        """
        Export all Monday.com data to a JSON file.
        
        Args:
            output_file: Path to the output file
            
        Returns:
            Dictionary containing all the data
        """
        logger.info("Starting Monday.com data export...")
        
        # Collect all data
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "account_info": {},
            "workspaces": [],
            "users": [],
            "boards": []
        }
        
        try:
            # Get account info
            logger.info("Fetching account information...")
            account_response = self.get_account_info()
            data["account_info"] = account_response.get("data", {})
            
            # Get workspaces
            logger.info("Fetching workspaces...")
            data["workspaces"] = self.get_workspaces()
            
            # Get users
            logger.info("Fetching users...")
            data["users"] = self.get_users()
            
            # Get all boards
            logger.info("Fetching all boards...")
            data["boards"] = self.get_all_boards()
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully exported {len(data['boards'])} boards to {output_file}")
            return data
            
        except Exception as e:
            logger.error(f"Error during data export: {e}")
            raise


def main():
    """Main function to run the Monday.com boards reader."""
    
    # Get API key from environment variable
    api_key = os.getenv("MONDAY_API_KEY")
    if not api_key:
        logger.error("Please set the MONDAY_API_KEY environment variable")
        return
    
    # Initialize the reader
    reader = MondayBoardsReader(api_key)
    
    # Export all data
    try:
        data = reader.export_all_data()
        print(f"Successfully exported Monday.com data!")
        print(f"Found {len(data['boards'])} boards")
        print(f"Found {len(data['workspaces'])} workspaces")
        print(f"Found {len(data['users'])} users")
        
    except Exception as e:
        logger.error(f"Failed to export data: {e}")


if __name__ == "__main__":
    main()