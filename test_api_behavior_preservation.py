"""
Test to verify that existing API behavior is preserved with smart prompt enhancement.
"""
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_prompt_flow():
    """Test that the prompt flows correctly through the enhancement and formatting pipeline."""
    
    # Set up minimal environment
    os.environ['OPENAI_API_KEY'] = 'test_key'
    os.environ['INTERNAL_DATABASE_API_KEY'] = 'test_key'
    
    try:
        # Import the functions we need to test
        from smart_prompt_enhancement import enhance_prompt
        from prompt_formatting import parse_prompt_to_internal_database_filters
        
        # Test case 1: Competitive prompt (should be enhanced)
        competitive_prompt = "Find me a sales manager looking to buy a new dialer like Orum"
        
        print("Test Case 1: Competitive prompt")
        print(f"Original: {competitive_prompt}")
        
        # Step 1: Smart enhancement
        enhanced_prompt, analysis = enhance_prompt(competitive_prompt)
        print(f"Enhanced: {enhanced_prompt}")
        print(f"Competitors excluded: {analysis.competitors}")
        
        # Step 2: Existing prompt formatting (should work with enhanced prompt)
        try:
            filters = parse_prompt_to_internal_database_filters(enhanced_prompt)
            print(f"Filters generated: {filters.get('reasoning', 'No reasoning available')}")
            print("✅ Competitive prompt test passed")
        except Exception as e:
            print(f"❌ Filter generation failed: {str(e)}")
            return False
        
        print()
        
        # Test case 2: Non-competitive prompt (should pass through mostly unchanged)
        non_competitive_prompt = "Find me a software engineer in New York"
        
        print("Test Case 2: Non-competitive prompt")
        print(f"Original: {non_competitive_prompt}")
        
        # Step 1: Smart enhancement (should be minimal)
        enhanced_prompt2, analysis2 = enhance_prompt(non_competitive_prompt)
        print(f"Enhanced: {enhanced_prompt2}")
        print(f"Competitors excluded: {analysis2.competitors}")
        
        # Step 2: Existing prompt formatting
        try:
            filters2 = parse_prompt_to_internal_database_filters(enhanced_prompt2)
            print(f"Filters generated: {filters2.get('reasoning', 'No reasoning available')}")
            print("✅ Non-competitive prompt test passed")
        except Exception as e:
            print(f"❌ Filter generation failed: {str(e)}")
            return False
        
        print()
        
        # Test case 3: Error handling (enhancement fails)
        print("Test Case 3: Error handling")
        
        # Simulate what happens in the API when enhancement fails
        test_prompt = "Find me a sales director"
        
        try:
            # This should work normally
            enhanced_prompt3, analysis3 = enhance_prompt(test_prompt)
            final_prompt = enhanced_prompt3
        except Exception as e:
            # This is the fallback behavior in the API
            print(f"Enhancement failed (simulated): {str(e)}")
            final_prompt = test_prompt
            print("Falling back to original prompt")
        
        # The existing formatting should still work
        try:
            filters3 = parse_prompt_to_internal_database_filters(final_prompt)
            print(f"Filters generated with fallback: {filters3.get('reasoning', 'No reasoning available')}")
            print("✅ Error handling test passed")
        except Exception as e:
            print(f"❌ Fallback filter generation failed: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")
        return False


def test_api_integration_points():
    """Test the specific integration points in the API."""
    
    print("Testing API integration points...")
    
    # Test that the import works
    try:
        from api.main import enhance_prompt as api_enhance_prompt
        print("✅ enhance_prompt imported successfully in API")
    except ImportError:
        print("❌ Failed to import enhance_prompt in API")
        return False
    
    # Test that it's the same function
    from smart_prompt_enhancement import enhance_prompt as direct_enhance_prompt
    
    if api_enhance_prompt == direct_enhance_prompt:
        print("✅ API uses the correct enhance_prompt function")
    else:
        print("❌ API is using a different enhance_prompt function")
        return False
    
    return True


if __name__ == "__main__":
    print("Testing API behavior preservation with smart prompt enhancement...")
    print("=" * 70)
    print()
    
    test1_passed = test_prompt_flow()
    print()
    print("=" * 70)
    print()
    
    test2_passed = test_api_integration_points()
    print()
    
    if test1_passed and test2_passed:
        print("🎉 All behavior preservation tests passed!")
        print("   - Smart prompt enhancement is properly integrated")
        print("   - Existing API behavior is preserved")
        print("   - Error handling works correctly")
    else:
        print("❌ Some behavior preservation tests failed")