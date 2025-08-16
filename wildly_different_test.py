#!/usr/bin/env python3
"""
Test script to demonstrate wildly different behavioral reasons
"""

from assess_and_return import _generate_realistic_behavioral_reasons
import json

def test_wildly_different_patterns():
    """Test that generates 20 different behavioral reason sets to show diversity"""
    
    print("WILDLY DIFFERENT BEHAVIORAL REASONS TEST")
    print("="*80)
    print("Testing 20 scenarios to demonstrate maximum diversity...")
    print("="*80)
    
    # Test scenarios with different roles and candidate indices
    test_scenarios = [
        ('Marketing Director', 'Find CMOs interested in CRM solutions', 0),
        ('Marketing Director', 'Find CMOs interested in CRM solutions', 1),
        ('Marketing Director', 'Find CMOs interested in CRM solutions', 2),
        ('Marketing Director', 'Find CMOs interested in CRM solutions', 3),
        ('Marketing Director', 'Find CMOs interested in CRM solutions', 4),
        ('Sales Manager', 'Find sales professionals looking for automation tools', 0),
        ('Sales Manager', 'Find sales professionals looking for automation tools', 1),
        ('Sales Manager', 'Find sales professionals looking for automation tools', 2),
        ('CTO', 'Find CTOs interested in cybersecurity solutions', 0),
        ('CTO', 'Find CTOs interested in cybersecurity solutions', 1),
        ('CTO', 'Find CTOs interested in cybersecurity solutions', 2),
        ('CEO', 'Find executives interested in business intelligence', 0),
        ('CEO', 'Find executives interested in business intelligence', 1),
        ('Chef', 'Find chefs interested in kitchen equipment', 0),
        ('Chef', 'Find chefs interested in kitchen equipment', 1),
        ('Data Scientist', 'Find data professionals interested in analytics', 0),
        ('Data Scientist', 'Find data professionals interested in analytics', 1),
        ('Product Manager', 'Find product managers looking for management tools', 0),
        ('DevOps Engineer', 'Find engineers interested in infrastructure automation', 0),
        ('Digital Marketing Manager', 'Find marketers looking for automation platforms', 0)
    ]
    
    all_reasons = []
    
    for i, (title, prompt, candidate_index) in enumerate(test_scenarios, 1):
        print(f"\nTest {i:2d}: {title} (Index: {candidate_index})")
        print(f"         Prompt: {prompt}")
        
        try:
            reasons = _generate_realistic_behavioral_reasons(title, prompt, candidate_index)
            print(f"         Reasons ({len(reasons)}):")
            for j, reason in enumerate(reasons, 1):
                print(f"           {j}. {reason}")
                all_reasons.append(reason)
        except Exception as e:
            print(f"         ERROR: {e}")
        
        print("-" * 80)
    
    # Analyze diversity
    print(f"\nDIVERSITY ANALYSIS")
    print("="*80)
    
    unique_reasons = len(set(all_reasons))
    total_reasons = len(all_reasons)
    diversity_percentage = (unique_reasons / total_reasons) * 100 if total_reasons > 0 else 0
    
    print(f"Total reasons generated: {total_reasons}")
    print(f"Unique reasons: {unique_reasons}")
    print(f"Diversity percentage: {diversity_percentage:.1f}%")
    
    # Check for any duplicates
    from collections import Counter
    reason_counts = Counter(all_reasons)
    duplicates = {reason: count for reason, count in reason_counts.items() if count > 1}
    
    if duplicates:
        print(f"\nDUPLICATES FOUND:")
        for reason, count in duplicates.items():
            print(f"  {count}x: {reason}")
    else:
        print(f"\n✅ NO DUPLICATES FOUND - All reasons are wildly different!")
    
    # Show variety in starting words
    starting_words = [reason.split()[0] for reason in all_reasons if reason.split()]
    starting_word_counts = Counter(starting_words)
    
    print(f"\nSTARTING WORD VARIETY:")
    for word, count in starting_word_counts.most_common():
        print(f"  {count}x: {word}")
    
    # Show website variety
    websites = []
    common_sites = ['.com', 'LinkedIn.com', 'TechCrunch.com', 'G2.com', 'Capterra.com', 
                   'Bloomberg.com', 'Forbes.com', 'Crunchbase.com', 'Stack Overflow']
    
    for reason in all_reasons:
        for site in common_sites:
            if site in reason:
                websites.append(site)
    
    website_counts = Counter(websites)
    print(f"\nWEBSITE MENTIONS:")
    for site, count in website_counts.most_common():
        print(f"  {count}x: {site}")
    
    print(f"\n" + "="*80)
    if diversity_percentage >= 95:
        print("🎉 EXCELLENT: Wildly different behavioral reasons achieved!")
    elif diversity_percentage >= 90:
        print("✅ VERY GOOD: High diversity in behavioral reasons")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Some repetition detected")
    print("="*80)

if __name__ == "__main__":
    test_wildly_different_patterns()