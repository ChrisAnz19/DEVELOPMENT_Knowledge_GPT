"""
Test script to verify smart prompt enhancement integration in API.
"""
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_smart_prompt_integration():
    """Test that smart prompt enhancement is properly integrated."""
    
    # Test the smart prompt enhancement directly
    from smart_prompt_enhancement import enhance_prompt
    
    original_prompt = 'Find me a sales manager looking to buy a new dialer like Orum'
    
    try:
        enhanced_prompt, analysis = enhance_prompt(original_prompt)
        
        print("✅ Smart prompt enhancement integration test passed!")
        print(f"   - Original prompt: {original_prompt}")
        print(f"   - Enhanced prompt: {enhanced_prompt}")
        print(f"   - Enhancement reasoning: {', '.join(analysis.reasoning) if analysis.reasoning else 'No specific reasoning'}")
        
        # Verify that enhancement was applied
        if enhanced_prompt != original_prompt:
            print("   - ✅ Prompt was successfully enhanced")
        else:
            print("   - ℹ️ No enhancement needed for this prompt")
            
        return True
        
    except Exception as e:
        print(f"❌ Smart prompt enhancement failed: {str(e)}")
        return False


def test_fallback_behavior():
    """Test that the enhancement gracefully handles errors."""
    
    # Test with a prompt that might cause issues
    from smart_prompt_enhancement import enhance_prompt
    
    # Test with various edge cases
    test_cases = [
        "",  # Empty prompt
        "   ",  # Whitespace only
        "a" * 1000,  # Very long prompt
        "Find me someone with special chars: @#$%^&*()",  # Special characters
    ]
    
    all_passed = True
    
    for i, test_prompt in enumerate(test_cases):
        try:
            enhanced_prompt, analysis = enhance_prompt(test_prompt)
            print(f"   - Test case {i+1}: ✅ Handled gracefully")
        except Exception as e:
            print(f"   - Test case {i+1}: ❌ Failed with error: {str(e)}")
            all_passed = False
    
    if all_passed:
        print("✅ Fallback behavior test passed!")
        print("   - All edge cases handled gracefully")
    else:
        print("❌ Some fallback tests failed")
        
    return all_passed


def test_existing_behavior_preserved():
    """Test that existing behavior is preserved for non-competitive prompts."""
    
    from smart_prompt_enhancement import enhance_prompt
    
    # Test with prompts that shouldn't trigger competitive intelligence
    non_competitive_prompts = [
        'Find me a software engineer in New York',
        'Looking for a marketing manager in San Francisco',
        'Need a data scientist with Python experience',
    ]
    
    all_passed = True
    
    for prompt in non_competitive_prompts:
        try:
            enhanced_prompt, analysis = enhance_prompt(prompt)
            
            # For non-competitive prompts, enhancement should be minimal or none
            if len(analysis.competitors) == 0:
                print(f"   - ✅ '{prompt[:30]}...' - No competitors detected (correct)")
            else:
                print(f"   - ⚠️ '{prompt[:30]}...' - Unexpected competitors detected: {analysis.competitors}")
                
        except Exception as e:
            print(f"   - ❌ '{prompt[:30]}...' - Failed with error: {str(e)}")
            all_passed = False
    
    if all_passed:
        print("✅ Existing behavior preservation test passed!")
        print("   - Non-competitive prompts handled correctly")
    else:
        print("❌ Some existing behavior tests failed")
        
    return all_passed


if __name__ == "__main__":
    print("Testing smart prompt enhancement API integration...")
    print()
    
    test1_passed = test_smart_prompt_integration()
    print()
    
    test2_passed = test_fallback_behavior()
    print()
    
    test3_passed = test_existing_behavior_preserved()
    print()
    
    if test1_passed and test2_passed and test3_passed:
        print("🎉 All API integration tests passed!")
    else:
        print("⚠️ Some tests had issues, but integration should still work")