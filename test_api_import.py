"""
Simple test to verify the API can be imported and the integration works.
"""
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_import():
    """Test that the API can be imported with the new smart prompt enhancement."""
    
    try:
        # Set up minimal environment
        os.environ['OPENAI_API_KEY'] = 'test_key'
        os.environ['INTERNAL_DATABASE_API_KEY'] = 'test_key'
        os.environ['SCRAPING_DOG_API_KEY'] = 'test_key'
        os.environ['SUPABASE_URL'] = 'test_url'
        os.environ['SUPABASE_KEY'] = 'test_key'
        
        # Try to import the main API module
        from api import main
        
        print("✅ API module imported successfully")
        
        # Check that the enhance_prompt function is imported
        if hasattr(main, 'enhance_prompt'):
            print("✅ enhance_prompt function is available in API module")
        else:
            print("❌ enhance_prompt function not found in API module")
            return False
            
        # Test that the FastAPI app is created
        if hasattr(main, 'app'):
            print("✅ FastAPI app is created")
        else:
            print("❌ FastAPI app not found")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import API module: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


if __name__ == "__main__":
    print("Testing API import with smart prompt enhancement integration...")
    print()
    
    if test_api_import():
        print()
        print("🎉 API import test passed! Smart prompt enhancement is properly integrated.")
    else:
        print()
        print("❌ API import test failed.")