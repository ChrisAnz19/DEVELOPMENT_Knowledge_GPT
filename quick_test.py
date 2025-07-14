#!/usr/bin/env python3
"""
Quick test script to demonstrate witty responses and error fixes
"""

from prompt_formatting import parse_prompt_to_apollo_filters, is_ridiculous_prompt, get_witty_error_response

def test_ridiculous_prompts():
    """Test ridiculous prompts to show witty responses"""
    ridiculous_prompts = [
        "a barista looking for enterprise cybersecurity",
        "a pizza delivery driver seeking quantum computing solutions",
        "a cashier at a gas station looking for machine learning tools",
        "a janitor wanting to implement blockchain technology"
    ]
    
    print("🎪 TESTING RIDICULOUS PROMPTS 🎪")
    print("=" * 60)
    
    for prompt in ridiculous_prompts:
        print(f"\n📝 Prompt: {prompt}")
        print(f"🤔 Is ridiculous: {is_ridiculous_prompt(prompt)}")
        
        if is_ridiculous_prompt(prompt):
            witty_response = get_witty_error_response()
            print(f"🎭 Response: {witty_response}")
        else:
            print("❌ Should have been detected as ridiculous!")
        
        print("-" * 40)

def test_normal_prompts():
    """Test normal prompts to verify they work"""
    normal_prompts = [
        "a sales director in new york looking to hire new sdrs",
        "a cto at a startup looking for a new crm",
        "a marketing manager looking for new marketing automation tools"
    ]
    
    print("\n✅ TESTING NORMAL PROMPTS ✅")
    print("=" * 60)
    
    for prompt in normal_prompts:
        print(f"\n📝 Prompt: {prompt}")
        print(f"🤔 Is ridiculous: {is_ridiculous_prompt(prompt)}")
        
        if not is_ridiculous_prompt(prompt):
            try:
                filters = parse_prompt_to_apollo_filters(prompt)
                print(f"✅ Filters generated successfully!")
                print(f"📋 Reasoning: {filters['reasoning']}")
                print(f"🏢 Org filters: {len(filters['organization_filters'])} items")
                print(f"👥 Person filters: {len(filters['person_filters'])} items")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ Should not have been detected as ridiculous!")
        
        print("-" * 40)

if __name__ == "__main__":
    test_ridiculous_prompts()
    test_normal_prompts()
    print("\n🎉 Quick test complete!") 