#!/usr/bin/env python3
"""
Knowledge_GPT Project Cleanup Script
Removes unnecessary files and organizes the project structure
"""

import os
import shutil
import glob

def cleanup_project():
    """Clean up the Knowledge_GPT project by removing unnecessary files"""
    
    print("🧹 KNOWLEDGE_GPT PROJECT CLEANUP")
    print("=" * 50)
    
    # Files to remove (test files, temporary files, etc.)
    files_to_remove = [
        # Test files
        "test_linkedin_data.py",
        "test_real_prompt.py", 
        "test_live_api.py",
        "test_render_deployment.py",
        "test_api.py",
        "test_pipeline.py",
        "quick_test.py",
        
        # Temporary files
        "test_results.json",
        "temp_filters.json",
        
        # Documentation files (keep README.md)
        "API_README.md",
        "RENDER_DEPLOYMENT.md",
        
        # Deployment files (keep essential ones)
        "deploy.sh",
        "docker-compose.yml",
        "Dockerfile",
        "Procfile",
        "runtime.txt",
        "setup.py",
        ".render-buildpacks",
        
        # System files
        ".DS_Store",
        
        # Old CLI main file (API version is in api/main.py)
        "main.py",
    ]
    
    # Directories to remove
    dirs_to_remove = [
        "__pycache__",
        ".venv",
        ".idea",
    ]
    
    # Remove files
    print("\n🗑️  Removing unnecessary files...")
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"   ✅ Removed: {file_path}")
            except Exception as e:
                print(f"   ❌ Failed to remove {file_path}: {e}")
        else:
            print(f"   ⏭️  Skipped (not found): {file_path}")
    
    # Remove directories
    print("\n🗂️  Removing unnecessary directories...")
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"   ✅ Removed: {dir_path}")
            except Exception as e:
                print(f"   ❌ Failed to remove {dir_path}: {e}")
        else:
            print(f"   ⏭️  Skipped (not found): {dir_path}")
    
    # Clean up any remaining cache files
    print("\n🧹 Cleaning up cache files...")
    cache_patterns = [
        "*.pyc",
        "*.pyo", 
        "__pycache__",
        ".pytest_cache",
        ".coverage",
        "*.log"
    ]
    
    for pattern in cache_patterns:
        for file_path in glob.glob(pattern):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"   ✅ Removed cache file: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"   ✅ Removed cache dir: {file_path}")
            except Exception as e:
                print(f"   ❌ Failed to remove {file_path}: {e}")
    
    # Create essential directories
    print("\n📁 Creating essential directories...")
    essential_dirs = [
        "search_results",
        "logs"
    ]
    
    for dir_path in essential_dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"   ✅ Created/verified: {dir_path}")
        except Exception as e:
            print(f"   ❌ Failed to create {dir_path}: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 CLEANUP COMPLETED!")
    print("=" * 50)
    
    # Show remaining files
    print("\n📋 Remaining project structure:")
    for root, dirs, files in os.walk("."):
        # Skip .git directory
        if ".git" in root:
            continue
            
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files:
            if not file.startswith("."):  # Skip hidden files
                print(f"{subindent}{file}")

if __name__ == "__main__":
    cleanup_project() 