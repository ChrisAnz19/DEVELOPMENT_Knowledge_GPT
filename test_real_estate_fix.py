#!/usr/bin/env python3
"""
Test to verify that real estate behavioral reasons now generate real estate URLs,
not CRM URLs.
"""

from explanation_analyzer import ExplanationAnalyzer
from alternative_source_manager import AlternativeSourceManager


def test_real_estate_behavioral_matching():
    """Test that real estate behavioral reasons are correctly identified and categorized."""
    print("Testing Real Estate Behavioral Matching:")
    print("=" * 60)
    
    analyzer = ExplanationAnalyzer()
    alt_manager = AlternativeSourceManager()
    
    # Real estate behavioral reasons (from your example)
    real_estate_reasons = [
        "Visited luxury real estate websites for Greenwich, Connecticut multiple times in the past month",
        "Engaged with financial calculators and mortgage rate comparison tools on real estate platforms",
        "Joined exclusive real estate investment forums discussing properties in Greenwich",
        "Saved multiple listings in Greenwich to favorites and shared them with a real estate agent"
    ]
    
    print("Testing real estate behavioral reasons:")
    print()
    
    for i, reason in enumerate(real_estate_reasons, 1):
        print(f"{i}. Reason: {reason}")
        
        # Extract claims
        claims = analyzer.extract_claims(reason)
        
        if claims:
            claim = claims[0]  # Take the first claim
            print(f"   Claim type: {claim.claim_type.value}")
            print(f"   Entities: {claim.entities}")
            
            # Identify category
            category = alt_manager.identify_category_from_claim(reason, claim.entities)
            print(f"   Identified category: {category}")
            
            # Check if it's correctly NOT CRM
            if claim.claim_type.value in ['real_estate_research', 'financial_services_research', 'investment_research']:
                print("   ✅ CORRECT: Identified as real estate/financial related")
            elif claim.claim_type.value in ['company_research', 'product_evaluation'] and 'crm' in claim.text.lower():
                print("   ❌ ERROR: Still identifying as CRM-related")
            else:
                print(f"   ⚠️  UNEXPECTED: Got {claim.claim_type.value}")
            
            # Get alternative sources for the identified category
            if category:
                alternatives = alt_manager.get_alternative_companies(category, count=3)
                print(f"   Alternative sources:")
                for alt in alternatives:
                    print(f"     - {alt.name} ({alt.domain}) [{alt.tier.value}]")
                    
                    # Verify these are real estate related, not CRM
                    if category == 'real_estate':
                        if any(term in alt.name.lower() for term in ['real', 'estate', 'property', 'realty', 'sotheby', 'compass', 'mansion']):
                            print(f"       ✅ CORRECT: {alt.name} is real estate related")
                        else:
                            print(f"       ❌ ERROR: {alt.name} doesn't seem real estate related")
                    elif category == 'financial_services':
                        if any(term in alt.name.lower() for term in ['bank', 'mortgage', 'lending', 'financial', 'nerd', 'rate']):
                            print(f"       ✅ CORRECT: {alt.name} is financial services related")
                        else:
                            print(f"       ❌ ERROR: {alt.name} doesn't seem financial services related")
            else:
                print("   ❌ ERROR: No category identified")
        else:
            print("   ❌ ERROR: No claims extracted")
        
        print()
    
    # Test a CRM example to make sure it still works
    print("Testing CRM behavioral reason (should still work):")
    crm_reason = "Currently researching CRM solutions for sales team management"
    print(f"CRM Reason: {crm_reason}")
    
    claims = analyzer.extract_claims(crm_reason)
    if claims:
        claim = claims[0]
        print(f"   Claim type: {claim.claim_type.value}")
        
        category = alt_manager.identify_category_from_claim(crm_reason, claim.entities)
        print(f"   Identified category: {category}")
        
        if category == 'crm':
            print("   ✅ CORRECT: CRM reason correctly identified as CRM")
            
            alternatives = alt_manager.get_alternative_companies(category, count=3)
            print(f"   CRM alternatives:")
            for alt in alternatives:
                print(f"     - {alt.name} ({alt.domain}) [{alt.tier.value}]")
        else:
            print(f"   ❌ ERROR: CRM reason identified as {category}")


if __name__ == '__main__':
    test_real_estate_behavioral_matching()