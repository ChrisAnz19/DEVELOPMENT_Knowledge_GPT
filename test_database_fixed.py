#!/usr/bin/env python3
"""
Test the fixed database functions to ensure they handle constraint violations properly.
"""

import unittest
import uuid
from datetime import datetime, timezone
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the fixed database functions
from database_fixed import (
    store_search_to_database, get_search_from_database,
    get_recent_searches_from_database, delete_search_from_database
)

class TestDatabaseFixed(unittest.TestCase):
    """Test the fixed database functions."""
    
    def setUp(self):
        """Set up test data."""
        self.request_id = str(uuid.uuid4())
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.search_data = {
            "request_id": self.request_id,
            "status": "processing",
            "prompt": "Test prompt",
            "filters": json.dumps({"test": "filter"}),
            "created_at": self.created_at,
            "completed_at": None
        }
    
    def test_store_new_search(self):
        """Test storing a new search."""
        # Store a new search
        search_id = store_search_to_database(self.search_data)
        
        # Verify the search was stored
        self.assertIsNotNone(search_id, "Failed to store new search")
        
        # Clean up
        delete_search_from_database(self.request_id)
    
    def test_update_existing_search(self):
        """Test updating an existing search."""
        # Store a new search
        search_id = store_search_to_database(self.search_data)
        self.assertIsNotNone(search_id, "Failed to store new search")
        
        # Get the search to verify it was stored
        search = get_search_from_database(self.request_id)
        self.assertIsNotNone(search, "Failed to retrieve stored search")
        
        # Update the search
        updated_data = {
            "request_id": self.request_id,
            "status": "completed",
            "prompt": "Updated prompt",
            "filters": json.dumps({"updated": "filter"}),
            "created_at": self.created_at,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Update using the same request_id (should find and update the existing record)
        updated_id = store_search_to_database(updated_data)
        self.assertIsNotNone(updated_id, "Failed to update search")
        
        # Get the updated search
        updated_search = get_search_from_database(self.request_id)
        self.assertIsNotNone(updated_search, "Failed to retrieve updated search")
        self.assertEqual(updated_search["status"], "completed", "Status not updated")
        self.assertEqual(updated_search["prompt"], "Updated prompt", "Prompt not updated")
        
        # Clean up
        delete_search_from_database(self.request_id)
    
    def test_update_with_id(self):
        """Test updating a search using its ID."""
        # Store a new search
        search_id = store_search_to_database(self.search_data)
        self.assertIsNotNone(search_id, "Failed to store new search")
        
        # Get the search to verify it was stored
        search = get_search_from_database(self.request_id)
        self.assertIsNotNone(search, "Failed to retrieve stored search")
        
        # Update the search using its ID
        updated_data = {
            "id": search["id"],
            "request_id": self.request_id,
            "status": "completed",
            "prompt": "Updated with ID",
            "filters": json.dumps({"updated": "with_id"}),
            "created_at": self.created_at,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Update using the ID
        updated_id = store_search_to_database(updated_data)
        self.assertIsNotNone(updated_id, "Failed to update search with ID")
        
        # Get the updated search
        updated_search = get_search_from_database(self.request_id)
        self.assertIsNotNone(updated_search, "Failed to retrieve updated search")
        self.assertEqual(updated_search["status"], "completed", "Status not updated")
        self.assertEqual(updated_search["prompt"], "Updated with ID", "Prompt not updated")
        
        # Clean up
        delete_search_from_database(self.request_id)
    
    def test_error_handling(self):
        """Test error handling for invalid data."""
        # Try to store a search without a request_id
        invalid_data = {
            "status": "processing",
            "prompt": "Invalid data",
            "created_at": self.created_at
        }
        
        result = store_search_to_database(invalid_data)
        self.assertIsNone(result, "Should return None for invalid data")

if __name__ == "__main__":
    unittest.main()