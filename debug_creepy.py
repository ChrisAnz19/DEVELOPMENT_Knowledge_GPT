#!/usr/bin/env python3
import re

def test_regex_patterns():
    prompt = 'Find me what websites Brett Markinson visited'
    print(f"Testing prompt: '{prompt}'")
    
    # Test the regex patterns from creepy_detector.py
    full_name_pattern = r'(?<!^)(?<!\. )\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
    full_names = re.findall(full_name_pattern, prompt)
    print(f"Full names found: {full_names}")
    
    start_name_pattern = r'^[A-Z][a-z]+\s+[A-Z][a-z]+\b'
    start_full_names = re.findall(start_name_pattern, prompt)
    print(f"Start names found: {start_full_names}")
    
    all_potential_names = full_names + start_full_names
    print(f"All potential names: {all_potential_names}")
    
    # Test if Brett Markinson should be detected
    if "Brett Markinson" in prompt:
        print("✅ 'Brett Markinson' is clearly in the prompt")
    
    # Test a simpler pattern
    simple_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
    simple_matches = re.findall(simple_pattern, prompt)
    print(f"Simple pattern matches: {simple_matches}")

if __name__ == "__main__":
    test_regex_patterns()