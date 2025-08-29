#!/usr/bin/env python3
"""
Test script to verify HRM platform context extraction works correctly.

This test checks that "HRM platforms" generates HR-related URLs, not political platform URLs.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from context_aware_evidence_finder import ContextAwareEvidenceFinder
    from behavioral_context_extractor import BehavioralContextExtractor
    print("Successfully imported modules")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


async def test_hrm_platform_context():
    """Test that HRM platform searches generate HR-related queries, not political ones."""
    
    print("🧪 Testing HRM Platform Context Extraction")
    print("=" * 50)
    
    # Test cases for HRM/HR platform searches
    test_cases = [
        {
            'prompt': 'Find me a HR manager looking for HRM platforms',
            'candidate': {
                'id': 'test_1',
                'name': 'Sarah Johnson',
                'title': 'HR Manager',
                'company': 'TechCorp Inc',
                'behavioral_data': {
                    'behavioral_insight': 'Sarah is researching HRM platforms for employee management'
                }
            },
            'expected_terms': ['hrm platform', 'hr platform', 'hris', 'workday'],
            'forbidden_terms': ['political', 'election', 'campaign', 'government']
        },
        {
            'prompt': 'Find me a CHRO evaluating HR platforms',
            'candidate': {
                'id': 'test_2',
                'name': 'Mike Chen',
                'title': 'Chief Human Resources Officer',
                'company': 'StartupXYZ',
                'behavioral_data': {
                    'behavioral_insight': 'Mike is comparing HR platforms for talent management'
                }
            },
            'expected_terms': ['hr platform', 'talent management', 'hris'],
            'forbidden_terms': ['political', 'election', 'campaign']
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\\n{i}. Testing: {test_case['prompt']}")
        
        # Test behavioral context extraction first
        extractor = BehavioralContextExtractor()
        behavioral_context = extractor.extract_behavioral_context(test_case['prompt'])
        
        print(f"   Behavioral Focus: '{behavioral_context.behavioral_focus}'")
        print(f"   Products: {behavioral_context.products}")
        print(f"   Technologies: {behavioral_context.technologies}")
        
        # Test context-aware evidence finder
        try:
            finder = ContextAwareEvidenceFinder(enable_diversity=True)
            finder.set_search_context(test_case['prompt'])
            
            queries = finder._generate_contextual_queries(test_case['candidate'])
            
            print(f"\\n   Generated {len(queries)} queries:")
            
            hr_related_count = 0
            political_count = 0
            
            for j, query in enumerate(queries, 1):
                print(f"     {j}. {query}")
                
                query_lower = query.lower()
                
                # Count HR-related terms
                if any(term.lower() in query_lower for term in test_case['expected_terms']):
                    hr_related_count += 1
                    print(f"        ✅ HR-RELATED: Contains expected HR terms")
                
                # Check for political terms (should be zero)
                if any(term.lower() in query_lower for term in test_case['forbidden_terms']):
                    political_count += 1
                    print(f"        ❌ POLITICAL: Contains political terms")
                
                # Check for generic "platform" without HR context
                if 'platform' in query_lower and not any(hr_term in query_lower for hr_term in ['hr', 'hrm', 'hris', 'human resources']):
                    print(f"        ⚠️  GENERIC: Contains 'platform' without HR context")
            
            # Evaluate results
            print(f"\\n   Results:")
            print(f"     HR-related queries: {hr_related_count}/{len(queries)}")
            print(f"     Political queries: {political_count}/{len(queries)}")
            
            if political_count == 0:
                print(f"     ✅ SUCCESS: No political platform queries generated")
            else:
                print(f"     ❌ FAILURE: {political_count} political queries found")
            
            if hr_related_count > 0:
                print(f"     ✅ SUCCESS: {hr_related_count} HR-related queries generated")
            else:
                print(f"     ⚠️  WARNING: No HR-specific context detected")
        
        except Exception as e:
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\\n" + "=" * 50)
    print(f"🎯 HRM Platform Context Test Complete!")
    print(f"\\nKey Success Metrics:")
    print(f"✅ Zero political platform queries")
    print(f"✅ HR-specific context preserved (HRM platforms, not generic platforms)")
    print(f"✅ Multi-word terms maintained in search queries")


def test_behavioral_context_extractor_directly():
    """Test the behavioral context extractor directly with HRM platform terms."""
    
    print("\\n🔍 Direct Behavioral Context Extractor Test")
    print("=" * 50)
    
    extractor = BehavioralContextExtractor()
    
    test_prompts = [
        "Find me a HR manager looking for HRM platforms",
        "Find executives evaluating HR platforms", 
        "Looking for CHRO researching HRIS platforms",
        "Find people interested in human resources platforms"
    ]
    
    for prompt in test_prompts:
        print(f"\\nPrompt: {prompt}")
        context = extractor.extract_behavioral_context(prompt)
        
        print(f"  Behavioral Focus: '{context.behavioral_focus}'")
        print(f"  Products: {context.products}")
        print(f"  Primary Focus: '{extractor.get_primary_behavioral_focus(context)}'")
        
        # Check if it preserves multi-word context
        if 'platform' in context.behavioral_focus and any(hr_term in context.behavioral_focus for hr_term in ['hrm', 'hr', 'hris', 'human resources']):
            print(f"  ✅ SUCCESS: Preserved HR platform context")
        elif 'platform' in context.behavioral_focus:
            print(f"  ❌ FAILURE: Generic platform without HR context")
        else:
            print(f"  ⚠️  INFO: No platform term detected")


if __name__ == "__main__":
    try:
        test_behavioral_context_extractor_directly()
        asyncio.run(test_hrm_platform_context())
    except Exception as e:
        print(f"Error running test: {e}")
        import traceback
        traceback.print_exc()