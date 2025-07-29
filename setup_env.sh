#!/bin/bash

# Load secrets from secrets.json and export as environment variables
if [ -f "secrets.json" ]; then
    echo "🔑 Loading secrets from secrets.json..."
    
    export SUPABASE_URL=$(python3 -c "import json; print(json.load(open('secrets.json'))['SUPABASE_URL'])")
    export SUPABASE_KEY=$(python3 -c "import json; print(json.load(open('secrets.json'))['SUPABASE_KEY'])")
    export OPENAI_API_KEY=$(python3 -c "import json; print(json.load(open('secrets.json'))['OPENAI_API_KEY'])")
    export INTERNAL_DATABASE_API_KEY=$(python3 -c "import json; print(json.load(open('secrets.json'))['INTERNAL_DATABASE_API_KEY'])")
    
    echo "✅ Environment variables set successfully"
    echo "🚀 You can now run: cd api && python3 main.py"
else
    echo "❌ secrets.json not found"
    exit 1
fi