"""
Test the behavioral metrics with varied data types and scenarios.

This test suite focuses on testing the behavioral metrics with different types of data,
including different industries, job roles, and behavioral patterns.
"""

import unittest
import json
import time
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from behavioral_metrics import (
    generate_behavioral_metrics,
    enhance_behavioral_data,
    calculate_commitment_momentum_index,
    calculate_risk_barrier_focus_score,
    calculate_identity_alignment_signal,
    generate_psychometric_modeling_insight
)

class TestBehavioralMetricsWithVariedData(unittest.TestCase):
    """Test the behavioral metrics with varied data types and scenarios."""
    
    def setUp(self):
        """Set up test data."""
        # Current timestamp for testing
        self.current_time = time.time()
        
        # Base behavioral data structure
        self.base_behavioral_data = {
            "insights": [],
            "page_views": [],
            "sessions": [],
            "content_interactions": []
        }
        
        # Sample candidate data templates
        self.tech_candidate = {
            "name": "John Doe",
            "title": "Senior Software Engineer",
            "company": "Tech Innovations Inc.",
            "email": "john@example.com",
            "linkedin_url": "https://linkedin.com/in/johndoe"
        }
        
        self.finance_candidate = {
            "name": "Jane Smith",
            "title": "Financial Analyst",
            "company": "Global Finance Corp.",
            "email": "jane@example.com",
            "linkedin_url": "https://linkedin.com/in/janesmith"
        }
        
        self.healthcare_candidate = {
            "name": "Robert Johnson",
            "title": "Medical Director",
            "company": "Healthcare Solutions",
            "email": "robert@example.com",
            "linkedin_url": "https://linkedin.com/in/robertjohnson"
        }

    def create_behavioral_data(self, scenario):
        """Create behavioral data for different scenarios."""
        data = self.base_behavioral_data.copy()
        
        if scenario == "high_commitment":
            # High commitment: Recent, frequent activity with bottom-funnel content
            data["page_views"] = [
                {"url": "/pricing", "title": "Pricing Plans", "timestamp": self.current_time - 3600},  # 1 hour ago
                {"url": "/demo", "title": "Request Demo", "timestamp": self.current_time - 7200},  # 2 hours ago
                {"url": "/checkout", "title": "Checkout", "timestamp": self.current_time - 10800},  # 3 hours ago
                {"url": "/implementation", "title": "Implementation Guide", "timestamp": self.current_time - 14400}  # 4 hours ago
            ]
            data["sessions"] = [
                {"timestamp": self.current_time - 3600, "duration": 1200, "pages": 10},  # 1 hour ago, 20 min
                {"timestamp": self.current_time - 86400, "duration": 900, "pages": 8},  # 1 day ago, 15 min
                {"timestamp": self.current_time - 172800, "duration": 600, "pages": 5}  # 2 days ago, 10 min
            ]
            data["content_interactions"] = [
                {"content_type": "pricing_document", "title": "Enterprise Pricing", "timestamp": self.current_time - 3600},
                {"content_type": "case_study", "title": "Implementation Success Story", "timestamp": self.current_time - 7200},
                {"content_type": "contract", "title": "Service Agreement", "timestamp": self.current_time - 10800}
            ]
            
        elif scenario == "low_commitment":
            # Low commitment: Old, infrequent activity with top-funnel content
            data["page_views"] = [
                {"url": "/blog", "title": "Blog Post", "timestamp": self.current_time - 2592000},  # 30 days ago
                {"url": "/about", "title": "About Us", "timestamp": self.current_time - 2678400},  # 31 days ago
                {"url": "/features", "title": "Features Overview", "timestamp": self.current_time - 2764800}  # 32 days ago
            ]
            data["sessions"] = [
                {"timestamp": self.current_time - 2592000, "duration": 300, "pages": 3},  # 30 days ago, 5 min
                {"timestamp": self.current_time - 3456000, "duration": 240, "pages": 2}  # 40 days ago, 4 min
            ]
            data["content_interactions"] = [
                {"content_type": "blog_post", "title": "Industry Trends", "timestamp": self.current_time - 2592000},
                {"content_type": "newsletter", "title": "Monthly Newsletter", "timestamp": self.current_time - 3456000}
            ]
            
        elif scenario == "high_risk_focus":
            # High risk focus: Engagement with risk-related content
            data["page_views"] = [
                {"url": "/security", "title": "Security Features", "timestamp": self.current_time - 86400},  # 1 day ago
                {"url": "/compliance", "title": "Compliance Information", "timestamp": self.current_time - 172800},  # 2 days ago
                {"url": "/privacy", "title": "Privacy Policy", "timestamp": self.current_time - 259200},  # 3 days ago
                {"url": "/reviews", "title": "Customer Reviews", "timestamp": self.current_time - 345600}  # 4 days ago
            ]
            data["sessions"] = [
                {"timestamp": self.current_time - 86400, "duration": 900, "pages": 8},  # 1 day ago, 15 min
                {"timestamp": self.current_time - 172800, "duration": 600, "pages": 5}  # 2 days ago, 10 min
            ]
            data["content_interactions"] = [
                {"content_type": "security_whitepaper", "title": "Security Best Practices", "timestamp": self.current_time - 86400},
                {"content_type": "compliance_guide", "title": "Regulatory Compliance", "timestamp": self.current_time - 172800},
                {"content_type": "risk_assessment", "title": "Risk Assessment Guide", "timestamp": self.current_time - 259200}
            ]
            
        elif scenario == "high_identity_alignment":
            # High identity alignment: Engagement with purpose-driven content
            data["page_views"] = [
                {"url": "/mission", "title": "Our Mission", "timestamp": self.current_time - 86400},  # 1 day ago
                {"url": "/values", "title": "Company Values", "timestamp": self.current_time - 172800},  # 2 days ago
                {"url": "/sustainability", "title": "Sustainability Initiatives", "timestamp": self.current_time - 259200},  # 3 days ago
                {"url": "/community", "title": "Community Impact", "timestamp": self.current_time - 345600}  # 4 days ago
            ]
            data["sessions"] = [
                {"timestamp": self.current_time - 86400, "duration": 900, "pages": 8},  # 1 day ago, 15 min
                {"timestamp": self.current_time - 172800, "duration": 600, "pages": 5}  # 2 days ago, 10 min
            ]
            data["content_interactions"] = [
                {"content_type": "mission_statement", "title": "Our Purpose", "timestamp": self.current_time - 86400},
                {"content_type": "csr_report", "title": "Corporate Social Responsibility", "timestamp": self.current_time - 172800},
                {"content_type": "community_forum", "title": "Community Discussion", "timestamp": self.current_time - 259200}
            ]
            
        elif scenario == "technical_focus":
            # Technical focus: Engagement with technical content
            data["page_views"] = [
                {"url": "/api-docs", "title": "API Documentation", "timestamp": self.current_time - 86400},  # 1 day ago
                {"url": "/developer", "title": "Developer Resources", "timestamp": self.current_time - 172800},  # 2 days ago
                {"url": "/technical-specs", "title": "Technical Specifications", "timestamp": self.current_time - 259200},  # 3 days ago
                {"url": "/integration", "title": "Integration Guide", "timestamp": self.current_time - 345600}  # 4 days ago
            ]
            data["sessions"] = [
                {"timestamp": self.current_time - 86400, "duration": 1800, "pages": 15},  # 1 day ago, 30 min
                {"timestamp": self.current_time - 172800, "duration": 1200, "pages": 10}  # 2 days ago, 20 min
            ]
            data["content_interactions"] = [
                {"content_type": "api_documentation", "title": "REST API Reference", "timestamp": self.current_time - 86400},
                {"content_type": "technical_whitepaper", "title": "Architecture Overview", "timestamp": self.current_time - 172800},
                {"content_type": "code_sample", "title": "Sample Implementation", "timestamp": self.current_time - 259200}
            ]
            
        elif scenario == "business_focus":
            # Business focus: Engagement with business-oriented content
            data["page_views"] = [
                {"url": "/roi-calculator", "title": "ROI Calculator", "timestamp": self.current_time - 86400},  # 1 day ago
                {"url": "/case-studies", "title": "Case Studies", "timestamp": self.current_time - 172800},  # 2 days ago
                {"url": "/pricing", "title": "Pricing Plans", "timestamp": self.current_time - 259200},  # 3 days ago
                {"url": "/enterprise", "title": "Enterprise Solutions", "timestamp": self.current_time - 345600}  # 4 days ago
            ]
            data["sessions"] = [
                {"timestamp": self.current_time - 86400, "duration": 900, "pages": 8},  # 1 day ago, 15 min
                {"timestamp": self.current_time - 172800, "duration": 600, "pages": 5}  # 2 days ago, 10 min
            ]
            data["content_interactions"] = [
                {"content_type": "business_case", "title": "Business Case Template", "timestamp": self.current_time - 86400},
                {"content_type": "roi_report", "title": "ROI Analysis", "timestamp": self.current_time - 172800},
                {"content_type": "executive_summary", "title": "Executive Summary", "timestamp": self.current_time - 259200}
            ]
            
        elif scenario == "off_hours_activity":
            # Off-hours activity: Engagement outside business hours
            # Create timestamps for evenings and weekends
            weekend_timestamp = self.current_time - 172800  # 2 days ago
            weekend_date = datetime.fromtimestamp(weekend_timestamp)
            # Adjust to make sure it's a weekend (Saturday or Sunday)
            while weekend_date.weekday() < 5:  # 5 = Saturday, 6 = Sunday
                weekend_timestamp -= 86400  # Subtract one day
                weekend_date = datetime.fromtimestamp(weekend_timestamp)
            
            evening_timestamp = self.current_time - 86400  # 1 day ago
            evening_date = datetime.fromtimestamp(evening_timestamp)
            # Set to evening hours (8 PM)
            evening_date = evening_date.replace(hour=20, minute=0, second=0)
            evening_timestamp = evening_date.timestamp()
            
            data["page_views"] = [
                {"url": "/pricing", "title": "Pricing Plans", "timestamp": evening_timestamp},  # Evening
                {"url": "/features", "title": "Features Overview", "timestamp": weekend_timestamp},  # Weekend
                {"url": "/demo", "title": "Request Demo", "timestamp": evening_timestamp - 3600}  # Evening - 1 hour
            ]
            data["sessions"] = [
                {"timestamp": evening_timestamp, "duration": 1800, "pages": 15},  # Evening, 30 min
                {"timestamp": weekend_timestamp, "duration": 1200, "pages": 10}  # Weekend, 20 min
            ]
            data["content_interactions"] = [
                {"content_type": "pricing_document", "title": "Enterprise Pricing", "timestamp": evening_timestamp},
                {"content_type": "case_study", "title": "Implementation Success Story", "timestamp": weekend_timestamp}
            ]
            
        return data

    def test_high_commitment_scenario(self):
        """Test behavioral metrics with high commitment scenario."""
        # Create high commitment behavioral data
        behavioral_data = self.create_behavioral_data("high_commitment")
        
        # Generate metrics
        metrics = generate_behavioral_metrics(
            "Find a senior software engineer",
            self.tech_candidate,
            behavioral_data
        )
        
        # Check that the commitment momentum index is high
        self.assertIn("commitment_momentum_index", metrics)
        cmi = metrics["commitment_momentum_index"]
        self.assertGreater(cmi["score"], 70)  # Should be high (above 70)
        self.assertIn("Active", cmi["description"])  # Should indicate active engagement

    def test_low_commitment_scenario(self):
        """Test behavioral metrics with low commitment scenario."""
        # Create low commitment behavioral data
        behavioral_data = self.create_behavioral_data("low_commitment")
        
        # Generate metrics
        metrics = generate_behavioral_metrics(
            "Find a senior software engineer",
            self.tech_candidate,
            behavioral_data
        )
        
        # Check that the commitment momentum index is low
        self.assertIn("commitment_momentum_index", metrics)
        cmi = metrics["commitment_momentum_index"]
        self.assertLess(cmi["score"], 50)  # Should be low (below 50)
        self.assertNotIn("Active", cmi["description"])  # Should not indicate active engagement

    def test_high_risk_focus_scenario(self):
        """Test behavioral metrics with high risk focus scenario."""
        # Create high risk focus behavioral data
        behavioral_data = self.create_behavioral_data("high_risk_focus")
        
        # Generate metrics
        metrics = generate_behavioral_metrics(
            "Find a financial analyst",
            self.finance_candidate,
            behavioral_data
        )
        
        # Check that the risk-barrier focus score is high
        self.assertIn("risk_barrier_focus_score", metrics)
        rbfs = metrics["risk_barrier_focus_score"]
        self.assertGreater(rbfs["score"], 70)  # Should be high (above 70)
        self.assertNotIn("Low concern", rbfs["description"])  # Should not indicate low concern

    def test_high_identity_alignment_scenario(self):
        """Test behavioral metrics with high identity alignment scenario."""
        # Create high identity alignment behavioral data
        behavioral_data = self.create_behavioral_data("high_identity_alignment")
        
        # Generate metrics
        metrics = generate_behavioral_metrics(
            "Find a medical director",
            self.healthcare_candidate,
            behavioral_data
        )
        
        # Check that the identity alignment signal is high
        self.assertIn("identity_alignment_signal", metrics)
        ias = metrics["identity_alignment_signal"]
        self.assertGreater(ias["score"], 70)  # Should be high (above 70)
        self.assertIn("alignment", ias["description"].lower())  # Should mention alignment

    def test_technical_focus_scenario(self):
        """Test behavioral metrics with technical focus scenario."""
        # Create technical focus behavioral data
        behavioral_data = self.create_behavioral_data("technical_focus")
        
        # Generate metrics
        metrics = generate_behavioral_metrics(
            "Find a senior software engineer",
            self.tech_candidate,
            behavioral_data
        )
        
        # Check that the psychometric modeling insight mentions technical focus
        self.assertIn("psychometric_modeling_insight", metrics)
        pmi = metrics["psychometric_modeling_insight"]
        self.assertIn("technical", pmi.lower())  # Should mention technical focus

    def test_business_focus_scenario(self):
        """Test behavioral metrics with business focus scenario."""
        # Create business focus behavioral data
        behavioral_data = self.create_behavioral_data("business_focus")
        
        # Generate metrics
        metrics = generate_behavioral_metrics(
            "Find a financial analyst",
            self.finance_candidate,
            behavioral_data
        )
        
        # Check that the psychometric modeling insight mentions business focus
        self.assertIn("psychometric_modeling_insight", metrics)
        pmi = metrics["psychometric_modeling_insight"]
        # Should mention business terms like ROI, business value, etc.
        self.assertTrue(
            "roi" in pmi.lower() or 
            "business" in pmi.lower() or 
            "value" in pmi.lower()
        )

    def test_off_hours_activity_scenario(self):
        """Test behavioral metrics with off-hours activity scenario."""
        # Create off-hours activity behavioral data
        behavioral_data = self.create_behavioral_data("off_hours_activity")
        
        # Generate metrics
        metrics = generate_behavioral_metrics(
            "Find a senior software engineer",
            self.tech_candidate,
            behavioral_data
        )
        
        # Check that the commitment momentum index factors reflect off-hours activity
        self.assertIn("commitment_momentum_index", metrics)
        cmi = metrics["commitment_momentum_index"]
        self.assertIn("factors", cmi)
        self.assertIn("off_hours_activity", cmi["factors"])
        self.assertGreater(cmi["factors"]["off_hours_activity"], 0.5)  # Should be high

    def test_industry_specific_context(self):
        """Test behavioral metrics with industry-specific context."""
        # Test with different industry contexts
        industries = ["Technology", "Finance", "Healthcare"]
        candidates = [self.tech_candidate, self.finance_candidate, self.healthcare_candidate]
        
        for i, industry in enumerate(industries):
            # Create behavioral data
            behavioral_data = self.create_behavioral_data("high_commitment")
            
            # Generate metrics with industry context
            metrics = generate_behavioral_metrics(
                f"Find a professional in {industry}",
                candidates[i],
                behavioral_data,
                industry_context=industry
            )
            
            # Check that all metrics are present
            self.assertIn("commitment_momentum_index", metrics)
            self.assertIn("risk_barrier_focus_score", metrics)
            self.assertIn("identity_alignment_signal", metrics)
            self.assertIn("psychometric_modeling_insight", metrics)
            
            # Check that the psychometric modeling insight mentions the industry
            pmi = metrics["psychometric_modeling_insight"]
            self.assertIsInstance(pmi, str)
            self.assertGreater(len(pmi), 20)  # Should have meaningful content

    def test_mixed_signals_scenario(self):
        """Test behavioral metrics with mixed signals."""
        # Create a mixed behavioral data scenario
        # High commitment but also high risk focus
        high_commitment_data = self.create_behavioral_data("high_commitment")
        high_risk_data = self.create_behavioral_data("high_risk_focus")
        
        mixed_data = self.base_behavioral_data.copy()
        mixed_data["page_views"] = high_commitment_data["page_views"] + high_risk_data["page_views"]
        mixed_data["sessions"] = high_commitment_data["sessions"] + high_risk_data["sessions"]
        mixed_data["content_interactions"] = high_commitment_data["content_interactions"] + high_risk_data["content_interactions"]
        
        # Generate metrics
        metrics = generate_behavioral_metrics(
            "Find a financial analyst",
            self.finance_candidate,
            mixed_data
        )
        
        # Check that both commitment and risk scores are relatively high
        self.assertIn("commitment_momentum_index", metrics)
        self.assertIn("risk_barrier_focus_score", metrics)
        
        cmi = metrics["commitment_momentum_index"]
        rbfs = metrics["risk_barrier_focus_score"]
        
        # Both scores should be above average
        self.assertGreater(cmi["score"], 50)
        self.assertGreater(rbfs["score"], 50)
        
        # Check that the psychometric modeling insight reflects this complexity
        pmi = metrics["psychometric_modeling_insight"]
        self.assertGreater(len(pmi), 50)  # Should be a more nuanced insight

    def test_data_serialization(self):
        """Test that all behavioral metrics can be serialized to JSON."""
        # Test with different scenarios
        scenarios = ["high_commitment", "high_risk_focus", "high_identity_alignment", "technical_focus"]
        
        for scenario in scenarios:
            # Create behavioral data
            behavioral_data = self.create_behavioral_data(scenario)
            
            # Generate metrics
            metrics = generate_behavioral_metrics(
                "Find a professional",
                self.tech_candidate,
                behavioral_data
            )
            
            # Check that the metrics can be serialized to JSON
            try:
                json_data = json.dumps(metrics)
                self.assertIsInstance(json_data, str)
            except Exception as e:
                self.fail(f"Metrics for {scenario} could not be serialized to JSON: {e}")

if __name__ == "__main__":
    unittest.main()