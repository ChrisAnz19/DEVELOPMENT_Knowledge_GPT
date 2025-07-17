import asyncio
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the fixed modules
from linkedin_scraping_fixed import async_scrape_linkedin_profiles

class AsyncTestCase(unittest.TestCase):
    """Base class for async test cases."""
    
    def run_async(self, coro):
        """Run an async coroutine in the event loop."""
        return asyncio.run(coro)

class TestAsyncFixes(AsyncTestCase):
    """Test the fixes for async/await usage."""

    @patch('linkedin_scraping_fixed.httpx.AsyncClient')
    def test_async_scrape_linkedin_profiles_with_list(self, mock_client):
        """Test that async_scrape_linkedin_profiles properly handles lists."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "Test User", "headline": "Test Headline"}
        
        # Setup mock client
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.get.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        async def test_coroutine():
            # Test with a list of URLs
            urls = ["https://www.linkedin.com/in/testuser1", "https://www.linkedin.com/in/testuser2"]
            result = await async_scrape_linkedin_profiles(urls)
            
            # Verify the function returned a list
            self.assertIsInstance(result, list)
            # Verify the function made the expected number of calls
            self.assertEqual(mock_client_instance.__aenter__.return_value.get.call_count, 2)
        
        self.run_async(test_coroutine())
    
    @patch('linkedin_scraping_fixed.httpx.AsyncClient')
    def test_async_scrape_linkedin_profiles_with_string(self, mock_client):
        """Test that async_scrape_linkedin_profiles handles a single string URL."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "Test User", "headline": "Test Headline"}
        
        # Setup mock client
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.get.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        async def test_coroutine():
            # Test with a single URL string
            url = "https://www.linkedin.com/in/testuser"
            result = await async_scrape_linkedin_profiles(url)
            
            # Verify the function returned a list
            self.assertIsInstance(result, list)
            # Verify the function made one call
            self.assertEqual(mock_client_instance.__aenter__.return_value.get.call_count, 1)
        
        self.run_async(test_coroutine())
    
    @patch('linkedin_scraping_fixed.httpx.AsyncClient')
    def test_async_scrape_linkedin_profiles_with_empty_list(self, mock_client):
        """Test that async_scrape_linkedin_profiles handles an empty list."""
        # Setup mock client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        async def test_coroutine():
            # Test with an empty list
            urls = []
            result = await async_scrape_linkedin_profiles(urls)
            
            # Verify the function returned an empty list
            self.assertEqual(result, [])
            # Verify the function didn't make any calls
            self.assertEqual(mock_client_instance.__aenter__.return_value.get.call_count if hasattr(mock_client_instance.__aenter__, 'return_value') else 0, 0)
        
        self.run_async(test_coroutine())
    
    @patch('linkedin_scraping_fixed.httpx.AsyncClient')
    def test_async_scrape_linkedin_profiles_with_none(self, mock_client):
        """Test that async_scrape_linkedin_profiles handles None."""
        # Setup mock client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        async def test_coroutine():
            # Test with None
            urls = None
            result = await async_scrape_linkedin_profiles(urls)
            
            # Verify the function returned an empty list
            self.assertEqual(result, [])
            # Verify the function didn't make any calls
            self.assertEqual(mock_client_instance.__aenter__.return_value.get.call_count if hasattr(mock_client_instance.__aenter__, 'return_value') else 0, 0)
        
        self.run_async(test_coroutine())
    
    @patch('linkedin_scraping_fixed.httpx.AsyncClient')
    def test_async_scrape_linkedin_profiles_with_error(self, mock_client):
        """Test that async_scrape_linkedin_profiles handles errors properly."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        # Setup mock client
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.get.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        async def test_coroutine():
            # Test with a list of URLs
            urls = ["https://www.linkedin.com/in/testuser"]
            result = await async_scrape_linkedin_profiles(urls)
            
            # Verify the function returned a list with an error object
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertIn("error", result[0])
        
        self.run_async(test_coroutine())

if __name__ == "__main__":
    unittest.main()