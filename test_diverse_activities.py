#!/usr/bin/env python3
"""
Test script to verify diverse behavioral reason generation
"""

from assess_and_return import _generate_realistic_behavioral_reasons
import json

def test_diverse_activities():
    """Test the updated function with different roles and prompts"""
    
    test_cases = [
        ('Marketing Director', 'Find me a CMO interested in CRM solutions', 0),
        ('Chief Technology Officer', 'Find me a CTO looking for cybersecurity solutions', 1),
        ('Sales Manager', 'Find me sales professionals interested in sales automation tools', 2),
        ('CEO', 'Find me executives interested in business intelligence platforms', 0),
        ('Chef', 'Find me chefs interested in commercial kitchen equipment', 1),
        ('Software Engineer', 'Find me developers interested in cloud platforms', 2)
    ]

    print('Testing diverse behavioral reason generation:')
    print('=' * 60)

    for title, prompt, index in test_cases:
        print(f'\nRole: {title}')
        print(f'Prompt: {prompt}')
        print(f'Candidate Index: {index}')
        print('Reasons:')
        
        try:
            reasons = _generate_realistic_behavioral_reasons(title, prompt, index)
            for i, reason in enumerate(reasons, 1):
                print(f'  {i}. {reason}')
        except Exception as e:
            print(f'  Error: {e}')
        
        print('-' * 40)

    # Test for repetitive patterns
    print('\nTesting for repetitive patterns across multiple candidates:')
    print('=' * 60)
    
    all_reasons = []
    for i in range(5):  # Test 5 candidates
        reasons = _generate_realistic_behavioral_reasons('Marketing Director', 'Find me CMOs interested in CRM', i)
        all_reasons.extend(reasons)
        print(f'Candidate {i+1}: {reasons}')
    
    # Check for repetitive patterns
    repetitive_patterns = ['downloaded', 'whitepaper', 'webinar', 'attended']
    found_patterns = []
    
    for reason in all_reasons:
        for pattern in repetitive_patterns:
            if pattern.lower() in reason.lower():
                found_patterns.append((pattern, reason))
    
    if found_patterns:
        print(f'\nWARNING: Found repetitive patterns:')
        for pattern, reason in found_patterns:
            print(f'  Pattern "{pattern}" in: {reason}')
    else:
        print('\n✅ SUCCESS: No repetitive patterns found!')

if __name__ == "__main__":
    test_diverse_activities()