#!/usr/bin/env python3
"""
Debug Real Estate Query Issue.

This script debugs why the query "Find me an executive looking to buy a new home in Greenwich, Connecticut"
is returning irrelevant procurement/purchasing executive URLs instead of real estate URLs.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LocationContext:
    """Context for location-based searches."""
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None


@dataclass
class SearchContext:
    """Represents the context of the original search."""
    search_prompt: str
    industry: Optional[str] = None
    role_type: Optional[str] = None
    activity_type: Optional[str] = None
    key_terms: List[str] = None
    
    def __post_init__(self):
        if self.key_terms is None:
            self.key_terms = []


def debug_search_context_analysis():
    """Debug the search context analysis for the real estate query."""
    print("Debugging Search Context Analysis")
    print("=" * 50)
    
    search_prompt = "Find me an executive looking to buy a new home in Greenwich, Connecticut"
    print(f"Search Prompt: {search_prompt}")
    print()
    
    # Test industry detection
    def _detect_industry(prompt: str) -> Optional[str]:
        """Detect industry from search prompt."""
        industry_patterns = {
            'media': r'\b(media|entertainment|broadcasting|publishing|content|streaming)\b',
            'technology': r'\b(tech|technology|software|saas|ai|digital|cloud)\b',
            'finance': r'\b(financial|finance|banking|investment|private equity|hedge fund)\b',
            'healthcare': r'\b(healthcare|medical|pharma|biotech|hospital)\b',
            'real_estate': r'\b(real estate|property|commercial|residential|reit|home|house|housing)\b',
            'retail': r'\b(retail|consumer|e-commerce|shopping|brand)\b',
            'manufacturing': r'\b(manufacturing|industrial|automotive|aerospace)\b',
            'energy': r'\b(energy|oil|gas|renewable|utilities)\b'
        }
        
        prompt_lower = prompt.lower()
        matches = []
        
        for industry, pattern in industry_patterns.items():
            if re.search(pattern, prompt_lower):
                matches.append(industry)
        
        print(f"Industry Pattern Matches: {matches}")
        return matches[0] if matches else None
    
    # Test role detection
    def _detect_role_type(prompt: str) -> Optional[str]:
        """Detect role type from search prompt."""
        role_patterns = {
            'corporate_development': r'\b(corporate development|m&a|mergers|acquisitions|divestiture)\b',
            'marketing': r'\b(marketing|cmo|brand|advertising|digital marketing)\b',
            'sales': r'\b(sales|business development|revenue|account)\b',
            'finance': r'\b(cfo|finance|accounting|controller|treasurer)\b',
            'operations': r'\b(operations|coo|supply chain|logistics)\b',
            'technology': r'\b(cto|engineering|developer|architect|devops)\b',
            'hr': r'\b(hr|human resources|talent|recruiting|chro)\b',
            'executive': r'\b(ceo|president|founder|executive|c-level)\b'
        }
        
        prompt_lower = prompt.lower()
        matches = []
        
        for role, pattern in role_patterns.items():
            if re.search(pattern, prompt_lower):
                matches.append(role)
        
        print(f"Role Pattern Matches: {matches}")
        return matches[0] if matches else None
    
    # Test activity detection
    def _detect_activity_type(prompt: str) -> Optional[str]:
        """Detect activity type from search prompt."""
        activity_patterns = {
            'considering': r'\b(considering|evaluating|exploring|looking at)\b',
            'implementing': r'\b(implementing|deploying|rolling out|adopting)\b',
            'researching': r'\b(researching|investigating|studying|analyzing)\b',
            'planning': r'\b(planning|preparing|strategizing|developing)\b',
            'buying': r'\b(buying|purchasing|acquiring|procuring|looking to buy|want to buy|need to buy|buy)\b',
            'selling': r'\b(selling|divesting|disposing|exiting)\b'
        }
        
        prompt_lower = prompt.lower()
        matches = []
        
        for activity, pattern in activity_patterns.items():
            if re.search(pattern, prompt_lower):
                matches.append(activity)
        
        print(f"Activity Pattern Matches: {matches}")
        return matches[0] if matches else None
    
    # Test search intent detection
    def _detect_search_intent(search_prompt: str) -> str:
        """Detect the intent of the search to generate appropriate queries."""
        intent_patterns = {
            'real_estate': r'\b(homes?|houses?|real estate|property|properties|listings?|MLS|for sale|buy|rent)\b',
            'business': r'\b(company|companies|business|corporation|firm|organization|office|headquarters)\b',
            'person': r'\b(people|person|executive|manager|director|CEO|CTO|CFO|VP|president)\b',
            'investment': r'\b(invest|investment|fund|capital|portfolio|equity|venture)\b',
            'technology': r'\b(software|tech|platform|SaaS|API|cloud|digital)\b'
        }
        
        matches = []
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, search_prompt, re.IGNORECASE):
                matches.append(intent)
        
        print(f"Search Intent Matches: {matches}")
        return matches[0] if matches else 'general'
    
    # Run all detections
    industry = _detect_industry(search_prompt)
    role_type = _detect_role_type(search_prompt)
    activity_type = _detect_activity_type(search_prompt)
    search_intent = _detect_search_intent(search_prompt)
    
    print()
    print("Final Analysis Results:")
    print(f"Industry: {industry}")
    print(f"Role Type: {role_type}")
    print(f"Activity Type: {activity_type}")
    print(f"Search Intent: {search_intent}")
    
    return {
        'industry': industry,
        'role_type': role_type,
        'activity_type': activity_type,
        'search_intent': search_intent
    }


def debug_location_extraction():
    """Debug location extraction from the search prompt."""
    print("\nDebugging Location Extraction")
    print("=" * 50)
    
    search_prompt = "Find me an executive looking to buy a new home in Greenwich, Connecticut"
    print(f"Search Prompt: {search_prompt}")
    
    def _extract_location_context(search_prompt: str) -> LocationContext:
        """Extract location context from search prompt."""
        location = LocationContext()
        
        # Common city patterns
        city_patterns = [
            r'\b(Greenwich|New York|Los Angeles|Chicago|Boston|Miami|Seattle|Austin|Denver)\b',
            r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',  # "in CityName"
            r'\b([A-Z][a-z]+)\s+(?:CT|NY|CA|TX|FL|MA|WA|CO)\b'  # "City ST"
        ]
        
        print("Testing city patterns:")
        for i, pattern in enumerate(city_patterns, 1):
            match = re.search(pattern, search_prompt, re.IGNORECASE)
            if match:
                city = match.group(1) if match.lastindex else match.group(0)
                print(f"  Pattern {i}: MATCH - '{city}'")
                if not location.city:
                    location.city = city
            else:
                print(f"  Pattern {i}: No match")
        
        # State patterns
        state_patterns = [
            r'\b(Connecticut|CT|New York|NY|California|CA|Texas|TX|Florida|FL)\b'
        ]
        
        print("\nTesting state patterns:")
        for i, pattern in enumerate(state_patterns, 1):
            match = re.search(pattern, search_prompt, re.IGNORECASE)
            if match:
                state = match.group(0)
                print(f"  Pattern {i}: MATCH - '{state}'")
                if not location.state:
                    location.state = state
            else:
                print(f"  Pattern {i}: No match")
        
        return location
    
    location = _extract_location_context(search_prompt)
    print(f"\nExtracted Location:")
    print(f"  City: {location.city}")
    print(f"  State: {location.state}")
    
    return location


def debug_query_generation():
    """Debug the query generation process."""
    print("\nDebugging Query Generation")
    print("=" * 50)
    
    search_prompt = "Find me an executive looking to buy a new home in Greenwich, Connecticut"
    location = LocationContext(city="Greenwich", state="Connecticut")
    
    def _generate_real_estate_queries(location: LocationContext) -> List[str]:
        """Generate specific real estate queries."""
        queries = []
        
        if location.city:
            base_location = location.city
            if location.state:
                base_location = f"{location.city} {location.state}"
            
            # Highly specific real estate queries
            specific_queries = [
                f"{base_location} homes for sale",
                f"{base_location} real estate listings",
                f"{base_location} MLS listings",
                f"{base_location} property listings current",
                f"{base_location} houses for sale by owner",
                f"{base_location} real estate market report 2024",
                f"{base_location} home prices current market",
                f"buy house {base_location}",
                f"{base_location} real estate agents",
                f"{base_location} property values trends"
            ]
            
            queries.extend(specific_queries)
        
        return queries
    
    # Test contextual query generation (the problematic one)
    def _generate_contextual_queries_problematic(search_prompt: str) -> List[str]:
        """Generate contextual queries that might be causing the issue."""
        queries = []
        
        # This is likely what's happening - the system is focusing on "executive" + "buying"
        # and generating procurement/purchasing queries instead of real estate queries
        
        # Simulate the problematic logic
        if "executive" in search_prompt.lower() and "buy" in search_prompt.lower():
            # WRONG: This generates procurement queries
            problematic_queries = [
                "executive purchasing decisions",
                "procurement executive responsibilities", 
                "purchasing executive job description",
                "executive buy-in strategies",
                "corporate purchasing executive roles"
            ]
            queries.extend(problematic_queries)
        
        return queries
    
    # Generate both types of queries
    real_estate_queries = _generate_real_estate_queries(location)
    problematic_queries = _generate_contextual_queries_problematic(search_prompt)
    
    print("CORRECT Real Estate Queries:")
    for i, query in enumerate(real_estate_queries, 1):
        print(f"  {i}. {query}")
    
    print("\nPROBLEMATIC Contextual Queries (likely what's being used):")
    for i, query in enumerate(problematic_queries, 1):
        print(f"  {i}. {query}")
    
    return {
        'real_estate_queries': real_estate_queries,
        'problematic_queries': problematic_queries
    }


def main():
    """Run all debugging tests."""
    print("Real Estate Query Debug Analysis")
    print("=" * 60)
    
    # Debug search context analysis
    context_results = debug_search_context_analysis()
    
    # Debug location extraction
    location_results = debug_location_extraction()
    
    # Debug query generation
    query_results = debug_query_generation()
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS")
    print("=" * 60)
    
    print("The issue is likely one of the following:")
    print()
    
    if context_results['search_intent'] == 'real_estate':
        print("✅ Search intent is correctly detected as 'real_estate'")
    else:
        print(f"❌ Search intent is incorrectly detected as '{context_results['search_intent']}'")
    
    if location_results.city:
        print(f"✅ Location is correctly extracted: {location_results.city}")
    else:
        print("❌ Location extraction failed")
    
    print()
    print("LIKELY ROOT CAUSE:")
    print("The system is probably using the fallback contextual query generation")
    print("instead of the specific real estate query generation, which is causing")
    print("it to focus on 'executive' + 'buying' = procurement queries instead of")
    print("'home buying in Greenwich' = real estate queries.")
    
    print()
    print("SOLUTION:")
    print("1. Ensure real estate intent detection takes priority")
    print("2. Fix the query generation logic to use location-specific queries")
    print("3. Add better context disambiguation for 'executive buying home' vs 'purchasing executive'")


if __name__ == "__main__":
    main()