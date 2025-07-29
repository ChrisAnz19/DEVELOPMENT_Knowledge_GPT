#!/usr/bin/env python3
"""
Script to load secrets from secrets.json and start the API server
"""

import os
import json
import subprocess
import sys

def load_secrets_to_env():
    """Load secrets from secrets.json into environment variables"""
    try:
        with open("secrets.json", "r") as f:
            secrets = json.load(f)
        
        # Set environment variables
        for key, value in secrets.items():
            os.environ[key] = value
            print(f"✅ Set {key}")
        
        print(f"🔑 Loaded {len(secrets)} secrets into environment")
        return True
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Failed to load secrets.json: {e}")
        return False

def start_api_server():
    """Start the FastAPI server"""
    try:
        print("🚀 Starting API server...")
        # Change to the api directory and start the server
        os.chdir("api")
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start API server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 API server stopped by user")
        return True

if __name__ == "__main__":
    print("🔧 Loading secrets and starting API server...")
    
    if load_secrets_to_env():
        start_api_server()
    else:
        print("💥 Cannot start API server without proper configuration")
        sys.exit(1)