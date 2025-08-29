#!/usr/bin/env python3
"""
Test script to verify behavioral query generation is working correctly.

This test checks that the context-aware evidence finder generates behavioral
queries focused on what prospects are looking for, not role definitions.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from context_aware_evidence_finder import ContextAwareEvidenceFinder
    print("Successfully imported ContextAwareEvidenceFinder")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


async def test_behavioral_query_generation():
    """Test that behavioral queries are generated instead of role-based queries."""
    
    print("🧪 Testing Behavioral Query Generation")
    print("=" * 50)
    
    # Test cases that were generating role-based URLs
    test_cases = [
        {
            'prompt': 'Find me a HR manager looking for HRIS solutions',
            'candidate': {
                'id': 'test_1',
                'name': 'Sarah Johnson',
                'title': 'HR Manager',
                'company': 'TechCorp Inc',
                'behavioral_data': {
                    'behavioral_insight': 'Sarah is researching HRIS platforms for employee management'
                }
            },
            'expected_focus': ['hris', 'solutions', 'implementation'],
            'forbidden_terms': ['hr manager', 'job description', 'responsibilities']
        },
        {
            'prompt': 'Find me a marketing director evaluating CRM systems',
            'candidate': {
                'id': 'test_2',
                'name': 'Mike Chen',
                'title': 'Marketing Director',
                'company': 'StartupXYZ',
                'behavioral_data': {
                    'behavioral_insight': 'Mike is comparing CRM solutions for lead management'
                }
            },
            'expected_focus': ['crm', 'systems', 'comparison'],
            'forbidden_terms': ['marketing director', 'duties', 'role']
        },
        {
            'prompt': 'Find me a CFO researching accounting software',
            'candidate': {
                'id': 'test_3',
                'name': 'Lisa Wang',
                'title': 'CFO',
                'company': 'GrowthCo',
                'behavioral_data': {
                    'behavioral_insight': 'Lisa is evaluating accounting software for financial reporting'
                }
            },
            'expected_focus': ['accounting', 'software', 'pricing'],
            'forbidden_terms': ['cfo', 'responsibilities', 'job description']
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\\n{i}. Testing: {test_case['prompt']}")
        print(f"   Candidate: {test_case['candidate']['title']} at {test_case['candidate']['company']}")
        
        try:
            # Initialize context-aware evidence finder
            finder = ContextAwareEvidenceFinder(enable_diversity=True)
            
            # Set search context
            finder.set_search_context(test_case['prompt'])
            
            # Generate contextual queries
            queries = finder._generate_contextual_queries(test_case['candidate'])
            
            print(f"\\n   Generated {len(queries)} queries:")
            
            behavioral_focus_count = 0
            role_definition_count = 0
            
            for j, query in enumerate(queries, 1):
                print(f"     {j}. {query}")
                
                # Check if query focuses on behavioral context
                query_lower = query.lower()
                
                # Count behavioral focus
                if any(focus_term.lower() in query_lower for focus_term in test_case['expected_focus']):
                    behavioral_focus_count += 1
                    print(f"        ✅ BEHAVIORAL: Focuses on expected terms")
                
                # Check for forbidden role-definition terms
                if any(forbidden.lower() in query_lower for forbidden in test_case['forbidden_terms']):
                    role_definition_count += 1
                    print(f"        ❌ ROLE-BASED: Contains forbidden terms")
                
                # Check for generic role patterns
                role_patterns = ['what is a', 'job description', 'responsibilities', 'duties', 'role of']
                if any(pattern in query_lower for pattern in role_patterns):
                    role_definition_count += 1
                    print(f"        ❌ GENERIC ROLE: Contains role definition pattern")
            
            # Evaluate results
            print(f"\\n   Results:")
            print(f"     Behavioral focus queries: {behavioral_focus_count}/{len(queries)}")
            print(f"     Role definition queries: {role_definition_count}/{len(queries)}")
            
            if role_definition_count == 0:
                print(f"     ✅ SUCCESS: No role-definition queries generated")
            else:
                print(f"     ❌ FAILURE: {role_definition_count} role-definition queries found")
            
            if behavioral_focus_count > 0:
                print(f"     ✅ SUCCESS: {behavioral_focus_count} behavioral queries generated")
            else:
                print(f"     ⚠️  WARNING: No behavioral focus detected")
        
        except Exception as e:
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(test_behavioral_query_generation())
    except Exception as e:
        print(f"Error running test: {e}")
        import traceback
        traceback.print_exc()