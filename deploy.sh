#!/bin/bash

# Knowledge_GPT API Deployment Script
# This script sets up and deploys the Knowledge_GPT API backend

set -e

echo "🚀 Knowledge_GPT API Deployment Script"
echo "======================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if secrets.json exists
if [ ! -f "secrets.json" ]; then
    echo "⚠️  secrets.json not found. Creating from template..."
    cp secrets_template.json secrets.json
    echo "📝 Please edit secrets.json with your API keys:"
    echo "   - OpenAI API key"
    echo "   - Apollo API key"
    echo "   - Bright Data API key (optional)"
    echo ""
    echo "Press Enter when you've updated secrets.json..."
    read
fi

# Build and start the containers
echo "🔨 Building and starting Knowledge_GPT API..."
docker-compose up --build -d

# Wait for the API to be ready
echo "⏳ Waiting for API to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 2
done

# Check if API is responding
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo ""
    echo "🎉 Knowledge_GPT API deployed successfully!"
    echo ""
    echo "📊 API Endpoints:"
    echo "   Health Check: http://localhost:8000/"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   Create Search: POST http://localhost:8000/api/search"
    echo "   Get Results: GET http://localhost:8000/api/search/{request_id}"
    echo ""
    echo "🔧 Management Commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop API: docker-compose down"
    echo "   Restart API: docker-compose restart"
    echo ""
    echo "🌐 Frontend Integration:"
    echo "   Use the React components in frontend/components/"
    echo "   API URL: http://localhost:8000"
else
    echo "❌ API failed to start. Check logs with: docker-compose logs"
    exit 1
fi 