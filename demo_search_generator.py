# type: ignore
"""
Demo Search Generator

This module provides an endpoint that generates AI-powered search examples
to demonstrate the endless possibilities and use cases of the platform.
Generates realistic search queries every 20 seconds to showcase potential applications.
"""

import json
import random
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import openai
import os
from typing import Dict, List, Any

app = Flask(__name__)
CORS(app)

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')

class DemoSearchGenerator:
    def __init__(self):
        self.search_categories = [
            "executive_recruitment", "technology_research", "investment_opportunities", 
            "vendor_evaluation", "market_expansion", "partnership_discovery",
            "talent_acquisition", "competitive_intelligence", "funding_search",
            "customer_acquisition", "solution_research", "merger_acquisition",
            "real_estate_commercial", "startup_discovery", "supplier_sourcing"
        ]
        
        self.industry_contexts = [
            "SaaS", "FinTech", "HealthTech", "EdTech", "E-commerce", "Manufacturing",
            "Real Estate", "Healthcare", "Financial Services", "Retail", "Consulting",
            "Media", "Automotive", "Energy", "Telecommunications", "Aerospace",
            "Logistics", "Construction", "Agriculture", "Biotechnology", "Gaming",
            "Cybersecurity", "AI/ML", "Blockchain", "IoT", "Robotics"
        ]
        
        self.geographic_regions = [
            "New York", "San Francisco", "Los Angeles", "Chicago", "Boston", "Austin",
            "Seattle", "Miami", "Denver", "Atlanta", "Dallas", "Philadelphia",
            "Washington DC", "San Diego", "Phoenix", "Las Vegas", "Portland", "Nashville",
            "Silicon Valley", "Research Triangle", "Detroit", "Houston", "Minneapolis"
        ]
        
        self.search_styles = [
            "casual", "formal", "urgent", "analytical", "conversational", "direct"
        ]

    def generate_search_example(self) -> Dict[str, Any]:
        """Generate a realistic search example using AI"""
        
        category = random.choice(self.search_categories)
        industry = random.choice(self.industry_contexts)
        location = random.choice(self.geographic_regions)
        style = random.choice(self.search_styles)
        
        prompt = f"""Generate a realistic search query that demonstrates advanced behavioral targeting capabilities. 

Context:
- Category: {category}
- Industry: {industry}  
- Location: {location}
- Writing Style: {style}

Create a search query that shows someone looking for a specific type of person based on their behavioral patterns, job role, and intent signals. Make it sound like it's written by a real person with the specified writing style.

Examples of diverse queries:
- "Manufacturing CIOs researching cloud ERP solutions"
- "People looking to invest in early stage venture funds"
- "Find me a CMO at a mid-size SaaS company who's been researching marketing automation tools"
- "Show me VPs of Sales in NYC who've been looking at CRM solutions"
- "Looking for executives showing signs of office expansion in Boston area"
- "Need to find startup founders in AI space seeking Series A funding"
- "Healthcare IT directors evaluating cybersecurity vendors"
- "Real estate developers researching sustainable building materials"

Writing styles:
- casual: relaxed, informal tone
- formal: professional, structured language  
- urgent: time-sensitive, action-oriented
- analytical: data-focused, precise
- conversational: friendly, natural speech
- direct: brief, to-the-point

Generate 1 unique, realistic search query that matches the style and context. Be creative and vary the approach. Return only the search query text, nothing else."""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.8
            )
            
            search_query = response.choices[0].message.content.strip()
            
            # Remove quotes if present
            if search_query.startswith('"') and search_query.endswith('"'):
                search_query = search_query[1:-1]
                
            return {
                "search_query": search_query,
                "category": category,
                "industry": industry,
                "location": location,
                "style": style,
                "timestamp": datetime.now().isoformat(),
                "use_case_type": self._determine_use_case_type(category),
                "refresh_interval": 11
            }
            
        except Exception as e:
            # Fallback to predefined examples if AI fails
            return self._get_fallback_search(category, industry, location)
    
    def _determine_use_case_type(self, category: str) -> str:
        """Determine the type of use case based on category"""
        use_case_mapping = {
            "executive_recruitment": "Talent Acquisition",
            "technology_research": "Technology Evaluation",
            "investment_opportunities": "Investment & Funding",
            "vendor_evaluation": "Procurement & Sourcing",
            "market_expansion": "Strategic Planning",
            "partnership_discovery": "Business Development",
            "talent_acquisition": "HR & Recruiting",
            "competitive_intelligence": "Market Research",
            "funding_search": "Investment & Funding",
            "customer_acquisition": "Sales & Marketing",
            "solution_research": "Technology Evaluation",
            "merger_acquisition": "Investment & M&A",
            "real_estate_commercial": "Commercial Real Estate",
            "startup_discovery": "Investment & Funding",
            "supplier_sourcing": "Procurement & Sourcing"
        }
        return use_case_mapping.get(category, "Business Intelligence")
    
    def _get_fallback_search(self, category: str, industry: str, location: str) -> Dict[str, Any]:
        """Fallback search examples if AI generation fails"""
        fallback_queries = [
            f"Manufacturing CIOs in {location} researching cloud ERP solutions",
            f"People looking to invest in early stage {industry} venture funds",
            f"Find me a Director of Marketing who's been researching {industry} automation tools",
            f"Show me CTOs at {industry} companies evaluating cybersecurity platforms",
            f"Looking for executives in {location} showing expansion signals in {industry}",
            f"Need VPs of Sales who've been attending {industry} trade conferences",
            f"Healthcare IT directors evaluating new {industry} vendor solutions",
            f"Startup founders in {industry} space seeking Series A funding in {location}",
            f"Real estate developers researching sustainable {industry} materials",
            f"Find decision makers researching {industry} digital transformation tools"
        ]
        
        style = random.choice(self.search_styles)
        
        return {
            "search_query": random.choice(fallback_queries),
            "category": category,
            "industry": industry,
            "location": location,
            "style": style,
            "timestamp": datetime.now().isoformat(),
            "use_case_type": self._determine_use_case_type(category),
            "refresh_interval": 11,
            "source": "fallback"
        }

# Initialize the generator
demo_generator = DemoSearchGenerator()

@app.route('/api/demo/search-example', methods=['GET'])
def get_search_example():
    """
    Generate a new AI-powered search example
    
    Returns:
        JSON response with search query and metadata
    """
    try:
        search_example = demo_generator.generate_search_example()
        
        return jsonify({
            "success": True,
            "data": search_example,
            "message": "Search example generated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to generate search example"
        }), 500

@app.route('/api/demo/search-stream', methods=['GET'])
def get_search_stream():
    """
    Get multiple search examples for continuous demo
    
    Query Parameters:
        count (int): Number of examples to generate (default: 5, max: 20)
    
    Returns:
        JSON response with array of search examples
    """
    try:
        count = min(int(request.args.get('count', 5)), 20)
        
        search_examples = []
        for _ in range(count):
            example = demo_generator.generate_search_example()
            search_examples.append(example)
            # Small delay to ensure different timestamps
            time.sleep(0.1)
        
        return jsonify({
            "success": True,
            "data": {
                "examples": search_examples,
                "total_count": len(search_examples),
                "generated_at": datetime.now().isoformat()
            },
            "message": f"Generated {len(search_examples)} search examples"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to generate search stream"
        }), 500

@app.route('/api/demo/categories', methods=['GET'])
def get_demo_categories():
    """
    Get available demo categories and contexts
    
    Returns:
        JSON response with available categories, industries, and locations
    """
    return jsonify({
        "success": True,
        "data": {
            "categories": demo_generator.search_categories,
            "industries": demo_generator.industry_contexts,
            "locations": demo_generator.geographic_regions
        },
        "message": "Demo categories retrieved successfully"
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)