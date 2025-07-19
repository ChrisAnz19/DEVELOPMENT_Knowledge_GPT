"""
Unit tests for competitive knowledge loader.
"""
import unittest
import json
import os
import tempfile
from competitive_knowledge_loader import (
    load_competitive_knowledge,
    get_company_competitors,
    get_category_info,
    find_company_category
)


class TestCompetitiveKnowledgeLoader(unittest.TestCase):
    
    def setUp(self):
        """Set up test data."""
        self.test_data = {
            "version": "1.0",
            "companies": {
                "orum": {
                    "category": "sales_dialer",
                    "competitors": ["five9", "outreach"],
                    "aliases": ["orum.com", "orum technologies"]
                },
                "salesforce": {
                    "category": "crm",
                    "competitors": ["hubspot", "pipedrive"],
                    "aliases": ["salesforce.com", "sfdc"]
                }
            },
            "categories": {
                "sales_dialer": {
                    "description": "Sales dialing platforms",
                    "buying_indicators": ["looking for dialer"],
                    "exclusion_patterns": ["dialer company"]
                }
            }
        }
    
    def test_load_competitive_knowledge_success(self):
        """Test successful loading of competitive knowledge."""
        # This test assumes the actual competitive_knowledge.json exists
        try:
            data = load_competitive_knowledge()
            self.assertIsInstance(data, dict)
            self.assertIn("companies", data)
            self.assertIn("categories", data)
        except FileNotFoundError:
            self.skipTest("competitive_knowledge.json not found")
    
    def test_get_company_competitors_direct_match(self):
        """Test getting competitors for a company with direct name match."""
        competitors = get_company_competitors("orum", self.test_data)
        self.assertEqual(competitors, ["five9", "outreach"])
    
    def test_get_company_competitors_alias_match(self):
        """Test getting competitors for a company using alias."""
        competitors = get_company_competitors("orum.com", self.test_data)
        self.assertEqual(competitors, ["five9", "outreach"])
    
    def test_get_company_competitors_case_insensitive(self):
        """Test that company lookup is case insensitive."""
        competitors = get_company_competitors("ORUM", self.test_data)
        self.assertEqual(competitors, ["five9", "outreach"])
    
    def test_get_company_competitors_not_found(self):
        """Test getting competitors for unknown company."""
        competitors = get_company_competitors("unknown_company", self.test_data)
        self.assertEqual(competitors, [])
    
    def test_get_category_info_found(self):
        """Test getting category information for existing category."""
        category_info = get_category_info("sales_dialer", self.test_data)
        expected = {
            "description": "Sales dialing platforms",
            "buying_indicators": ["looking for dialer"],
            "exclusion_patterns": ["dialer company"]
        }
        self.assertEqual(category_info, expected)
    
    def test_get_category_info_not_found(self):
        """Test getting category information for non-existent category."""
        category_info = get_category_info("unknown_category", self.test_data)
        self.assertEqual(category_info, {})
    
    def test_find_company_category_direct_match(self):
        """Test finding category for company with direct name match."""
        category = find_company_category("orum", self.test_data)
        self.assertEqual(category, "sales_dialer")
    
    def test_find_company_category_alias_match(self):
        """Test finding category for company using alias."""
        category = find_company_category("sfdc", self.test_data)
        self.assertEqual(category, "crm")
    
    def test_find_company_category_not_found(self):
        """Test finding category for unknown company."""
        category = find_company_category("unknown_company", self.test_data)
        self.assertIsNone(category)
    
    def test_error_handling_invalid_json(self):
        """Test error handling with invalid JSON data."""
        # Test with invalid data types
        competitors = get_company_competitors("orum", "invalid_data")
        self.assertEqual(competitors, [])
        
        category_info = get_category_info("sales_dialer", "invalid_data")
        self.assertEqual(category_info, {})
        
        category = find_company_category("orum", "invalid_data")
        self.assertIsNone(category)
    
    def test_error_handling_missing_keys(self):
        """Test error handling with missing keys in data."""
        incomplete_data = {"version": "1.0"}  # Missing companies and categories
        
        competitors = get_company_competitors("orum", incomplete_data)
        self.assertEqual(competitors, [])
        
        category_info = get_category_info("sales_dialer", incomplete_data)
        self.assertEqual(category_info, {})


if __name__ == '__main__':
    unittest.main()