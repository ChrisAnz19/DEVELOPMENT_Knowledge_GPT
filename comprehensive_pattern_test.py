#!/usr/bin/env python3
"""
Comprehensive test to run 20 behavioral reason generation tests
and analyze for any noticeable patterns or repetition.
"""

from assess_and_return import _generate_realistic_behavioral_reasons
import json
from collections import Counter
import re

def analyze_patterns(all_reasons):
    """Analyze behavioral reasons for patterns and repetition"""
    
    print("\n" + "="*80)
    print("PATTERN ANALYSIS RESULTS")
    print("="*80)
    
    # 1. Check for exact duplicates
    reason_counts = Counter(all_reasons)
    duplicates = {reason: count for reason, count in reason_counts.items() if count > 1}
    
    if duplicates:
        print(f"\n❌ EXACT DUPLICATES FOUND ({len(duplicates)} unique duplicates):")
        for reason, count in duplicates.items():
            print(f"  {count}x: {reason}")
    else:
        print("\n✅ NO EXACT DUPLICATES FOUND")
    
    # 2. Check for repetitive starting words/phrases
    starting_words = [reason.split()[0].lower() for reason in all_reasons if reason.split()]
    starting_word_counts = Counter(starting_words)
    frequent_starters = {word: count for word, count in starting_word_counts.items() if count > 8}  # More than 40% of 20 tests
    
    if frequent_starters:
        print(f"\n⚠️  FREQUENT STARTING WORDS (>40% usage):")
        for word, count in frequent_starters.items():
            print(f"  {count}/20 ({count*5}%): '{word.title()}'")
    else:
        print("\n✅ GOOD VARIETY IN STARTING WORDS")
    
    # 3. Check for repetitive key phrases
    problematic_phrases = [
        'downloaded', 'whitepaper', 'webinar', 'attended', 'viewed',
        'implementation guide', 'roi calculator', 'case study',
        'best practices', 'workflow optimization', 'professional development'
    ]
    
    found_problematic = {}
    for phrase in problematic_phrases:
        count = sum(1 for reason in all_reasons if phrase.lower() in reason.lower())
        if count > 0:
            found_problematic[phrase] = count
    
    if found_problematic:
        print(f"\n❌ PROBLEMATIC PHRASES FOUND:")
        for phrase, count in found_problematic.items():
            print(f"  {count}/20 ({count*5}%): '{phrase}'")
    else:
        print("\n✅ NO PROBLEMATIC PHRASES FOUND")
    
    # 4. Check for vendor/platform diversity
    vendors_mentioned = []
    common_vendors = ['salesforce', 'hubspot', 'microsoft', 'google', 'amazon', 'oracle', 'sap', 'adobe']
    for reason in all_reasons:
        for vendor in common_vendors:
            if vendor.lower() in reason.lower():
                vendors_mentioned.append(vendor)
    
    vendor_counts = Counter(vendors_mentioned)
    if vendor_counts:
        print(f"\n📊 VENDOR MENTIONS:")
        for vendor, count in vendor_counts.most_common():
            print(f"  {count}x: {vendor.title()}")
    
    # 5. Check activity verb diversity
    activity_verbs = []
    common_verbs = ['analyzed', 'evaluated', 'compared', 'researched', 'studied', 'investigated', 
                   'assessed', 'reviewed', 'examined', 'explored', 'monitored', 'tracked',
                   'validated', 'confirmed', 'verified', 'consulted', 'engaged', 'participated']
    
    for reason in all_reasons:
        for verb in common_verbs:
            if verb.lower() in reason.lower():
                activity_verbs.append(verb)
                break  # Only count first verb found per reason
    
    verb_counts = Counter(activity_verbs)
    print(f"\n📈 ACTIVITY VERB DISTRIBUTION:")
    for verb, count in verb_counts.most_common():
        print(f"  {count}x: {verb.title()}")
    
    # 6. Overall diversity score
    unique_reasons = len(set(all_reasons))
    total_reasons = len(all_reasons)
    diversity_score = (unique_reasons / total_reasons) * 100
    
    print(f"\n📊 OVERALL DIVERSITY METRICS:")
    print(f"  Unique reasons: {unique_reasons}/{total_reasons}")
    print(f"  Diversity score: {diversity_score:.1f}%")
    print(f"  Average reason length: {sum(len(r.split()) for r in all_reasons) / len(all_reasons):.1f} words")
    
    # 7. Final assessment
    print(f"\n" + "="*80)
    if diversity_score >= 95 and not duplicates and not found_problematic:
        print("🎉 EXCELLENT: High diversity, no problematic patterns detected!")
    elif diversity_score >= 90 and len(found_problematic) <= 1:
        print("✅ GOOD: Acceptable diversity with minimal pattern issues")
    elif diversity_score >= 80:
        print("⚠️  FAIR: Some patterns detected, room for improvement")
    else:
        print("❌ POOR: Significant pattern issues detected")
    print("="*80)

def run_comprehensive_test():
    """Run 20 different test scenarios and analyze results"""
    
    test_scenarios = [
        # CRM-related searches
        ('Marketing Director', 'Find me CMOs interested in CRM solutions', 0),
        ('Sales Manager', 'Find me sales professionals looking for CRM platforms', 1),
        ('VP of Sales', 'Find me executives interested in customer relationship management', 2),
        ('Business Development Manager', 'Find me professionals interested in CRM software', 0),
        
        # Technology searches
        ('Chief Technology Officer', 'Find me CTOs looking for cybersecurity solutions', 1),
        ('IT Director', 'Find me technology leaders interested in cloud platforms', 2),
        ('Software Engineer', 'Find me developers interested in development tools', 0),
        ('DevOps Engineer', 'Find me engineers looking for infrastructure automation', 1),
        
        # Marketing searches
        ('Chief Marketing Officer', 'Find me marketing executives interested in analytics platforms', 2),
        ('Digital Marketing Manager', 'Find me marketers looking for automation tools', 0),
        ('Content Marketing Manager', 'Find me content professionals interested in publishing platforms', 1),
        ('Growth Marketing Manager', 'Find me growth professionals looking for optimization tools', 2),
        
        # Executive searches
        ('CEO', 'Find me executives interested in business intelligence platforms', 0),
        ('Chief Financial Officer', 'Find me finance leaders looking for accounting software', 1),
        ('Chief Operating Officer', 'Find me operations executives interested in workflow tools', 2),
        ('President', 'Find me senior executives looking for enterprise solutions', 0),
        
        # Specialized searches
        ('Chef', 'Find me culinary professionals interested in kitchen equipment', 1),
        ('Restaurant Manager', 'Find me food service managers looking for POS systems', 2),
        ('Data Scientist', 'Find me data professionals interested in analytics platforms', 0),
        ('Product Manager', 'Find me product professionals looking for management tools', 1),
    ]
    
    print("COMPREHENSIVE BEHAVIORAL REASON PATTERN TEST")
    print("="*80)
    print(f"Running {len(test_scenarios)} test scenarios...")
    print("="*80)
    
    all_reasons = []
    test_results = []
    
    for i, (title, prompt, candidate_index) in enumerate(test_scenarios, 1):
        print(f"\nTest {i:2d}: {title}")
        print(f"         Prompt: {prompt}")
        print(f"         Index: {candidate_index}")
        
        try:
            reasons = _generate_realistic_behavioral_reasons(title, prompt, candidate_index)
            test_results.append({
                'test_number': i,
                'title': title,
                'prompt': prompt,
                'candidate_index': candidate_index,
                'reasons': reasons,
                'reason_count': len(reasons)
            })
            
            print(f"         Reasons ({len(reasons)}):")
            for j, reason in enumerate(reasons, 1):
                print(f"           {j}. {reason}")
                all_reasons.append(reason)
                
        except Exception as e:
            print(f"         ERROR: {e}")
            test_results.append({
                'test_number': i,
                'title': title,
                'prompt': prompt,
                'candidate_index': candidate_index,
                'error': str(e)
            })
        
        print("-" * 60)
    
    # Analyze all collected reasons
    if all_reasons:
        analyze_patterns(all_reasons)
        
        # Save detailed results
        with open('pattern_test_results.json', 'w') as f:
            json.dump({
                'test_scenarios': test_results,
                'total_reasons_generated': len(all_reasons),
                'unique_reasons': len(set(all_reasons)),
                'all_reasons': all_reasons
            }, f, indent=2)
        
        print(f"\n📁 Detailed results saved to: pattern_test_results.json")
    else:
        print("\n❌ No reasons were generated to analyze!")

if __name__ == "__main__":
    run_comprehensive_test()