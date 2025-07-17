import unittest
import json
import asyncio
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api.main_error_handling import app, DatabaseError, ExternalAPIError, DataProcessingError

class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
        self.assertEqual(data["version"], "1.0.0")
        
    @patch("api.main_error_handling.store_search_to_database")
    @patch("api.main_error_handling.process_search")
    def test_create_search_success(self, mock_process, mock_store):
        """Test successful search creation."""
        mock_store.return_value = "123"
        
        response = self.client.post(
            "/api/search",
            json={"prompt": "Find sales directors at tech companies"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "processing")
        self.assertEqual(data["prompt"], "Find sales directors at tech companies")
        self.assertIn("request_id", data)
        self.assertIn("created_at", data)
        
        # Verify background task was added
        mock_process.assert_called_once()
        
    def test_create_search_validation_error(self):
        """Test validation error handling in search creation."""
        # Empty prompt
        response = self.client.post(
            "/api/search",
            json={"prompt": ""}
        )
        self.assertEqual(response.status_code, 400)
        
        # Invalid max_candidates
        response = self.client.post(
            "/api/search",
            json={"prompt": "Find sales directors", "max_candidates": 0}
        )
        self.assertEqual(response.status_code, 400)
        
    @patch("api.main_error_handling.store_search_to_database")
    def test_create_search_database_error(self, mock_store):
        """Test database error handling in search creation."""
        mock_store.side_effect = Exception("Database connection failed")
        
        response = self.client.post(
            "/api/search",
            json={"prompt": "Find sales directors at tech companies"}
        )
        
        # Should still succeed since we continue processing even if DB storage fails
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "processing")
        
    @patch("api.main_error_handling.get_search_from_database")
    def test_get_search_result_not_found(self, mock_get):
        """Test handling of non-existent search."""
        mock_get.return_value = None
        
        response = self.client.get("/api/search/00000000-0000-0000-0000-000000000000")
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["detail"], "Search not found")
        
    @patch("api.main_error_handling.get_search_from_database")
    def test_get_search_result_database_error(self, mock_get):
        """Test database error handling in get search result."""
        mock_get.side_effect = Exception("Database connection failed")
        
        response = self.client.get("/api/search/00000000-0000-0000-0000-000000000000")
        
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertEqual(data["error"], "Database operation failed")
        
    def test_get_search_result_invalid_id(self):
        """Test handling of invalid search ID."""
        response = self.client.get("/api/search/invalid-uuid")
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["detail"], "Invalid request_id format")
        
    @patch("api.main_error_handling.get_search_from_database")
    @patch("api.main_error_handling.get_people_for_search")
    def test_get_search_result_json_parsing(self, mock_people, mock_get):
        """Test JSON parsing error handling in get search result."""
        # Setup mock to return search with invalid JSON
        mock_get.return_value = {
            "id": 1,
            "request_id": "00000000-0000-0000-0000-000000000000",
            "status": "completed",
            "prompt": "Find sales directors",
            "filters": "{invalid-json}",
            "behavioral_data": "{also-invalid}",
            "created_at": "2023-01-01T00:00:00Z",
            "completed_at": "2023-01-01T00:01:00Z"
        }
        
        mock_people.return_value = []
        
        response = self.client.get("/api/search/00000000-0000-0000-0000-000000000000")
        
        # Should succeed with empty objects for invalid JSON
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["filters"], {})
        self.assertEqual(data["behavioral_data"], {})
        
    @patch("api.main_error_handling.get_recent_searches_from_database")
    def test_list_searches_database_error(self, mock_get):
        """Test database error handling in list searches."""
        mock_get.side_effect = Exception("Database connection failed")
        
        response = self.client.get("/api/search")
        
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertEqual(data["error"], "Database operation failed")
        
    @patch("api.main_error_handling.delete_search_from_database")
    def test_delete_search_database_error(self, mock_delete):
        """Test database error handling in delete search."""
        mock_delete.side_effect = Exception("Database connection failed")
        
        response = self.client.delete("/api/search/00000000-0000-0000-0000-000000000000")
        
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertEqual(data["error"], "Database operation failed")
        
    @patch("api.main_error_handling.get_recent_searches_from_database")
    @patch("api.main_error_handling.get_current_exclusions")
    def test_get_database_stats_partial_failure(self, mock_exclusions, mock_searches):
        """Test partial failure handling in database stats."""
        mock_searches.return_value = [
            {"id": 1, "candidates": [1, 2, 3]},
            {"id": 2, "candidates": [4, 5]}
        ]
        mock_exclusions.side_effect = Exception("Failed to get exclusions")
        
        response = self.client.get("/api/database/stats")
        
        # Should succeed with available data
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["database_status"], "connected")
        self.assertEqual(data["total_searches"], 2)
        self.assertEqual(data["total_candidates"], 5)
        self.assertEqual(data["total_exclusions"], 0)
        
    @patch("api.main_error_handling.get_current_exclusions")
    def test_get_exclusions_database_error(self, mock_get):
        """Test database error handling in get exclusions."""
        mock_get.side_effect = Exception("Database connection failed")
        
        response = self.client.get("/api/exclusions")
        
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertEqual(data["error"], "Database operation failed")
        
    @patch("api.main_error_handling.process_search")
    def test_process_search_error_handling(self, mock_process):
        """Test error handling in process_search background task."""
        # This is a bit tricky to test directly since it's a background task
        # We'll just verify it doesn't raise exceptions
        mock_process.side_effect = Exception("Processing failed")
        
        # This should not raise an exception
        response = self.client.post(
            "/api/search",
            json={"prompt": "Find sales directors at tech companies"}
        )
        
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()