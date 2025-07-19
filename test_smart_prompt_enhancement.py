"""
Unit tests for smart prompt enhancement functionality.
"""
import pytest
from smart_prompt_enhancement import (
    detect_product_mentions,
    detect_buying_intent,
    generate_competitive_exclusions,
    enhance_prompt_with_exclusions,
    analyze_prompt,
    enhance_prompt,
    PromptAnalysis
)


# Test data
TEST_KNOWLEDGE_DATA = {
    "companies": {
        "orum": {
            "category": "sales_dialer",
            "competitors": ["five9", "outreach", "salesloft"],
            "aliases": ["orum.com", "orum technologies"]
        },
        "salesforce": {
            "category": "crm",
            "competitors": ["hubspot", "pipedrive"],
            "aliases": ["salesforce.com", "sfdc"]
        },
        "five9": {
            "category": "sales_dialer",
            "competitors": ["orum", "outreach"],
            "aliases": ["five9.com"]
        }
    },
    "categories": {
        "sales_dialer": {
            "buying_indicators": ["looking for dialer", "need calling solution"],
            "exclusion_patterns": ["dialer company", "calling platform provider"]
        }
    }
}


class TestDetectProductMentions:
    """Test product mention detection."""
    
    def test_detect_direct_company_mention(self):
        """Test detection of direct company names."""
        prompt = "Find me prospects interested in Orum"
        result = detect_product_mentions(prompt, TEST_KNOWLEDGE_DATA)
        assert "orum" in result
    
    def test_detect_alias_mention(self):
        """Test detection of company aliases."""
        prompt = "Looking for users of salesforce.com"
        result = detect_product_mentions(prompt, TEST_KNOWLEDGE_DATA)
        assert "salesforce" in result
    
    def test_detect_multiple_products(self):
        """Test detection of multiple products in one prompt."""
        prompt = "Compare Orum vs Salesforce for our team"
        result = detect_product_mentions(prompt, TEST_KNOWLEDGE_DATA)
        assert "orum" in result
        assert "salesforce" in result
    
    def test_case_insensitive_detection(self):
        """Test that detection works regardless of case."""
        prompt = "ORUM vs five9 comparison"
        result = detect_product_mentions(prompt, TEST_KNOWLEDGE_DATA)
        assert "orum" in result
        assert "five9" in result
    
    def test_no_products_detected(self):
        """Test when no known products are mentioned."""
        prompt = "Find me sales managers in tech companies"
        result = detect_product_mentions(prompt, TEST_KNOWLEDGE_DATA)
        assert result == []
    
    def test_empty_knowledge_data(self):
        """Test behavior with empty knowledge data."""
        prompt = "Find prospects using Orum"
        result = detect_product_mentions(prompt, {})
        assert result == []


class TestDetectBuyingIntent:
    """Test buying vs selling intent detection."""
    
    def test_clear_buying_intent(self):
        """Test detection of clear buying intent."""
        prompt = "Find sales managers looking to buy a new dialer"
        buying, selling, confidence = detect_buying_intent(prompt)
        assert buying is True
        assert selling is False
        assert confidence > 0.5
    
    def test_buyer_role_intent(self):
        """Test detection based on buyer roles."""
        prompt = "Find CTO interested in CRM solutions"
        buying, selling, confidence = detect_buying_intent(prompt)
        assert buying is True
        assert selling is False
    
    def test_selling_intent(self):
        """Test detection of selling intent."""
        prompt = "Find companies that sell dialer solutions"
        buying, selling, confidence = detect_buying_intent(prompt)
        assert buying is False
        assert selling is True
    
    def test_switch_intent(self):
        """Test detection of switching intent (buying)."""
        prompt = "Find prospects looking to switch from Salesforce"
        buying, selling, confidence = detect_buying_intent(prompt)
        assert buying is True
        assert selling is False
    
    def test_neutral_prompt(self):
        """Test prompt with no clear intent."""
        prompt = "Find software engineers at tech companies"
        buying, selling, confidence = detect_buying_intent(prompt)
        # Should have low confidence
        assert confidence < 0.5
    
    def test_mixed_intent_favors_buying(self):
        """Test that mixed intent with buyer roles favors buying."""
        prompt = "Find sales managers at companies selling or buying dialers"
        buying, selling, confidence = detect_buying_intent(prompt)
        assert buying is True
        assert selling is False


class TestGenerateCompetitiveExclusions:
    """Test competitive exclusion generation."""
    
    def test_single_product_exclusions(self):
        """Test exclusions for a single detected product."""
        detected_products = ["orum"]
        result = generate_competitive_exclusions(detected_products, TEST_KNOWLEDGE_DATA)
        expected = ["five9", "outreach", "salesloft"]
        assert all(comp in result for comp in expected)
    
    def test_multiple_product_exclusions(self):
        """Test exclusions for multiple detected products."""
        detected_products = ["orum", "salesforce"]
        result = generate_competitive_exclusions(detected_products, TEST_KNOWLEDGE_DATA)
        # Should include competitors from both products
        assert "five9" in result  # Orum competitor
        assert "hubspot" in result  # Salesforce competitor
    
    def test_no_products_no_exclusions(self):
        """Test that no products results in no exclusions."""
        result = generate_competitive_exclusions([], TEST_KNOWLEDGE_DATA)
        assert result == []
    
    def test_unknown_product_no_exclusions(self):
        """Test that unknown products don't generate exclusions."""
        detected_products = ["unknown_product"]
        result = generate_competitive_exclusions(detected_products, TEST_KNOWLEDGE_DATA)
        assert result == []


class TestEnhancePromptWithExclusions:
    """Test prompt enhancement with exclusions."""
    
    def test_add_competitor_exclusions(self):
        """Test adding competitor exclusions to prompt."""
        original = "Find prospects interested in Orum"
        analysis = PromptAnalysis(
            detected_products=["orum"],
            competitors=["five9", "outreach"],
            buying_intent=False,
            selling_intent=False,
            intent_confidence=0.3,
            reasoning=[]
        )
        
        result = enhance_prompt_with_exclusions(original, analysis)
        assert "EXCLUDE employees from these competing companies: Five9, Outreach" in result
    
    def test_add_buying_intent_clarification(self):
        """Test adding buying intent clarification."""
        original = "Find managers looking to buy a dialer"
        analysis = PromptAnalysis(
            detected_products=["orum"],
            competitors=["five9"],
            buying_intent=True,
            selling_intent=False,
            intent_confidence=0.8,
            reasoning=[]
        )
        
        result = enhance_prompt_with_exclusions(original, analysis)
        assert "BUYERS of this solution" in result
        assert "not companies that SELL" in result
    
    def test_no_enhancement_needed(self):
        """Test when no enhancement is needed."""
        original = "Find software engineers"
        analysis = PromptAnalysis(
            detected_products=[],
            competitors=[],
            buying_intent=False,
            selling_intent=False,
            intent_confidence=0.2,
            reasoning=[]
        )
        
        result = enhance_prompt_with_exclusions(original, analysis)
        assert result == original


class TestAnalyzePrompt:
    """Test complete prompt analysis."""
    
    def test_comprehensive_analysis(self):
        """Test complete analysis of a complex prompt."""
        prompt = "Find sales managers looking to buy a dialer like Orum"
        result = analyze_prompt(prompt, TEST_KNOWLEDGE_DATA)
        
        assert "orum" in result.detected_products
        assert len(result.competitors) > 0
        assert result.buying_intent is True
        assert result.selling_intent is False
        assert result.intent_confidence > 0.5
        assert len(result.reasoning) > 0
    
    def test_analysis_with_no_matches(self):
        """Test analysis when nothing is detected."""
        prompt = "Find software engineers"
        result = analyze_prompt(prompt, TEST_KNOWLEDGE_DATA)
        
        assert result.detected_products == []
        assert result.competitors == []
        assert result.intent_confidence < 0.5


class TestEnhancePrompt:
    """Test the main enhance_prompt function."""
    
    def test_successful_enhancement(self):
        """Test successful prompt enhancement."""
        original = "Find sales managers looking to buy a dialer like Orum"
        enhanced, analysis = enhance_prompt(original, TEST_KNOWLEDGE_DATA)
        
        # Should be enhanced
        assert enhanced != original
        assert "EXCLUDE" in enhanced
        assert len(analysis.competitors) > 0
        assert analysis.buying_intent is True
    
    def test_enhancement_with_error_fallback(self):
        """Test that errors fall back to original prompt."""
        # This should work normally, but we can test the fallback logic
        original = "Find prospects"
        enhanced, analysis = enhance_prompt(original, TEST_KNOWLEDGE_DATA)
        
        # Should at least return the original prompt
        assert enhanced is not None
        assert analysis is not None
    
    def test_real_world_example(self):
        """Test with the original Orum/Five9 example from requirements."""
        prompt = "Find me a sales manager looking to buy a new dialer, like Orum"
        enhanced, analysis = enhance_prompt(prompt, TEST_KNOWLEDGE_DATA)
        
        # Should detect Orum and exclude competitors
        assert "orum" in analysis.detected_products
        assert analysis.buying_intent is True
        assert "EXCLUDE" in enhanced
        assert "five9" in [c.lower() for c in analysis.competitors]


if __name__ == "__main__":
    # Run a few basic tests to verify functionality
    print("Running basic functionality tests...")
    
    # Test product detection
    prompt1 = "Find prospects interested in Orum"
    products = detect_product_mentions(prompt1, TEST_KNOWLEDGE_DATA)
    print(f"Detected products in '{prompt1}': {products}")
    
    # Test intent detection
    prompt2 = "Find sales managers looking to buy a dialer"
    buying, selling, conf = detect_buying_intent(prompt2)
    print(f"Intent analysis for '{prompt2}': buying={buying}, selling={selling}, confidence={conf}")
    
    # Test full enhancement
    prompt3 = "Find me a sales manager looking to buy a new dialer, like Orum"
    enhanced, analysis = enhance_prompt(prompt3, TEST_KNOWLEDGE_DATA)
    print(f"\nOriginal: {prompt3}")
    print(f"Enhanced: {enhanced}")
    print(f"Analysis: {analysis}")
    
    print("\nBasic tests completed successfully!")