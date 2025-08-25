#!/usr/bin/env python3
"""
Specific Search Query Generator.

Generates highly specific search queries instead of generic ones.
Addresses the issue where "homes in Greenwich" returns generic Zillow/Redfin
instead of specific property listings.
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
class SearchSpecificity:
    """Configuration for search specificity levels."""
    level: int  # 1=generic, 5=highly specific
    include_modifiers: bool = True
    include_location_details: bool = True
    include_time_context: bool = True


class SpecificSearchQueryGenerator:
    """Generates highly specific search queries for better evidence finding."""
    
    def __init__(self):
        self.location_patterns = {
            'real_estate': [
                '{location} homes for sale',
                '{location} real estate listings',
                '{location} property listings MLS',
                '{location} houses for sale by owner',
                '{location} real estate market report',
                '{location} home prices current',
                '{location} real estate agents',
                '{location} property values 2024'
            ],
            'business': [
                '{company} {location} office',
                '{company} {location} headquarters',
                '{company} {location} employees',
                '{company} {location} news',
                '{company} {location} press release'
            ],
            'person': [
                '"{name}" {company} LinkedIn',
                '"{name}" {company} biography',
                '"{name}" {title} {company}',
                '"{name}" {company} executive team',
                '"{name}" {company} press release'
            ]
        }
        
        self.industry_specific_terms = {
            'real_estate': ['MLS', 'listing', 'property', 'homes', 'houses', 'condos', 'market report'],
            'technology': ['software', 'platform', 'API', 'cloud', 'SaaS', 'tech stack'],
            'finance': ['investment', 'portfolio', 'fund', 'capital', 'banking', 'fintech'],
            'healthcare': ['medical', 'hospital', 'clinic', 'pharmaceutical', 'biotech'],
            'media': ['content', 'publishing', 'streaming', 'broadcast', 'digital media']
        }
    
    def generate_location_specific_queries(self, search_prompt: str, candidate: Dict[str, Any]) -> List[str]:
        """Generate location-specific search queries."""
        queries = []
        
        # Extract location information
        location_context = self._extract_location_context(search_prompt, candidate)
        
        # Detect search intent
        search_intent = self._detect_search_intent(search_prompt)
        
        if search_intent == 'real_estate' and location_context.city:
            queries.extend(self._generate_real_estate_queries(location_context))
        elif search_intent == 'business':
            queries.extend(self._generate_business_queries(search_prompt, candidate, location_context))
        elif search_intent == 'person':
            queries.extend(self._generate_person_queries(candidate, location_context))
        else:
            # Generic but still specific queries
            queries.extend(self._generate_contextual_queries(search_prompt, candidate))
        
        return queries[:5]  # Limit to top 5 most specific queries
    
    def _extract_location_context(self, search_prompt: str, candidate: Dict[str, Any]) -> LocationContext:
        """Extract location context from search prompt and candidate data."""
        location = LocationContext()
        
        # Common city patterns
        city_patterns = [
            r'\b(Greenwich|New York|Los Angeles|Chicago|Boston|Miami|Seattle|Austin|Denver)\b',
            r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',  # "in CityName"
            r'\b([A-Z][a-z]+)\s+(?:CT|NY|CA|TX|FL|MA|WA|CO)\b'  # "City ST"
        ]
        
        for pattern in city_patterns:
            match = re.search(pattern, search_prompt, re.IGNORECASE)
            if match:
                location.city = match.group(1) if match.lastindex else match.group(0)
                break
        
        # Extract from candidate data if not found in prompt
        if not location.city and candidate.get('company'):
            company = candidate['company']
            # Look for location in company name or description
            if 'Greenwich' in company:
                location.city = 'Greenwich'
                location.state = 'CT'
        
        # State patterns
        state_patterns = [
            r'\b(CT|NY|CA|TX|FL|MA|WA|CO|Connecticut|New York|California|Texas|Florida|Massachusetts|Washington|Colorado)\b'
        ]
        
        for pattern in state_patterns:
            match = re.search(pattern, search_prompt, re.IGNORECASE)
            if match:
                location.state = match.group(0)
                break
        
        return location
    
    def _detect_search_intent(self, search_prompt: str) -> str:
        """Detect the intent of the search to generate appropriate queries."""
        intent_patterns = {
            'real_estate': r'\b(homes?|houses?|real estate|property|properties|listings?|MLS|for sale|buy|rent)\b',
            'business': r'\b(company|companies|business|corporation|firm|organization|office|headquarters)\b',
            'person': r'\b(people|person|executive|manager|director|CEO|CTO|CFO|VP|president)\b',
            'investment': r'\b(invest|investment|fund|capital|portfolio|equity|venture)\b',
            'technology': r'\b(software|tech|platform|SaaS|API|cloud|digital)\b'
        }
        
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, search_prompt, re.IGNORECASE):
                return intent
        
        return 'general'
    
    def _generate_real_estate_queries(self, location: LocationContext) -> List[str]:
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
    
    def _generate_business_queries(self, search_prompt: str, candidate: Dict[str, Any], location: LocationContext) -> List[str]:
        """Generate specific business queries."""
        queries = []
        
        company = candidate.get('company', '')
        name = candidate.get('name', '')
        title = candidate.get('title', '')
        
        if company:
            # Company-specific queries
            queries.extend([
                f'"{company}" headquarters',
                f'"{company}" executive team',
                f'"{company}" press releases',
                f'"{company}" company profile',
                f'"{company}" leadership team'
            ])
            
            if location.city:
                queries.extend([
                    f'"{company}" {location.city} office',
                    f'"{company}" {location.city} location'
                ])
        
        if name and company:
            # Person at company queries
            queries.extend([
                f'"{name}" "{company}" LinkedIn',
                f'"{name}" {company} biography',
                f'"{name}" {company} executive'
            ])
        
        return queries
    
    def _generate_person_queries(self, candidate: Dict[str, Any], location: LocationContext) -> List[str]:
        """Generate specific person queries."""
        queries = []
        
        name = candidate.get('name', '')
        company = candidate.get('company', '')
        title = candidate.get('title', '')
        
        if name:
            # Person-specific queries
            queries.extend([
                f'"{name}" LinkedIn profile',
                f'"{name}" professional biography',
                f'"{name}" executive profile'
            ])
            
            if company:
                queries.extend([
                    f'"{name}" "{company}"',
                    f'"{name}" {company} LinkedIn',
                    f'"{name}" {company} executive team',
                    f'"{name}" {company} biography'
                ])
            
            if title:
                queries.extend([
                    f'"{name}" {title}',
                    f'"{name}" {title} {company}' if company else f'"{name}" {title}'
                ])
        
        return queries
    
    def _generate_contextual_queries(self, search_prompt: str, candidate: Dict[str, Any]) -> List[str]:
        """Generate contextual queries for general searches."""
        queries = []
        
        # Extract key terms from prompt
        key_terms = self._extract_key_terms(search_prompt)
        
        # Generate combinations of key terms
        if len(key_terms) >= 2:
            queries.append(f"{key_terms[0]} {key_terms[1]}")
        
        if len(key_terms) >= 3:
            queries.append(f"{key_terms[0]} {key_terms[1]} {key_terms[2]}")
        
        # Add candidate-specific context
        name = candidate.get('name', '')
        company = candidate.get('company', '')
        
        # REMOVED: Name-based queries that return irrelevant personal websites
        # These queries were causing the system to return websites that are just
        # variations of the prospect's name instead of behavioral evidence.
        # 
        # OLD CODE (REMOVED):
        # if name and any(term in search_prompt.lower() for term in ['people', 'person', 'executive']):
        #     queries.append(f'"{name}" professional profile')
        #
        # NEW APPROACH: Focus only on behavioral evidence, never use prospect names
        
        if company and any(term in search_prompt.lower() for term in ['company', 'business', 'firm']):
            queries.append(f'"{company}" company information')
        
        return queries
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text."""
        # Remove common words
        common_words = {
            'find', 'people', 'who', 'are', 'at', 'in', 'with', 'for', 'the', 'and', 'or', 'of', 'to', 'a', 'an',
            'is', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Extract words (3+ characters)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        key_terms = [word for word in words if word not in common_words]
        
        return key_terms[:5]  # Top 5 key terms
    
    def refine_generic_queries(self, initial_results: List[Dict[str, Any]], original_query: str) -> List[str]:
        """Refine queries when initial results are too generic."""
        refined_queries = []
        
        # Check if results are too generic (e.g., just homepage URLs)
        generic_indicators = ['homepage', 'home', 'index', 'main', 'www.', '.com/', '.com$']
        
        generic_count = 0
        for result in initial_results:
            url = result.get('url', '').lower()
            title = result.get('title', '').lower()
            
            if any(indicator in url or indicator in title for indicator in generic_indicators):
                generic_count += 1
        
        # If more than 50% of results are generic, refine the query
        if generic_count > len(initial_results) * 0.5:
            # Add more specific terms
            refined_queries.extend([
                f"{original_query} specific",
                f"{original_query} detailed",
                f"{original_query} current",
                f"{original_query} 2024",
                f'"{original_query}" exact'
            ])
        
        return refined_queries
    
    def score_result_specificity(self, result: Dict[str, Any]) -> float:
        """Score how specific a search result is (0.0 = generic, 1.0 = highly specific)."""
        url = result.get('url', '').lower()
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        specificity_score = 0.5  # Base score
        
        # Positive indicators (increase specificity)
        specific_indicators = [
            'listing', 'profile', 'biography', 'details', 'information', 'report', 'analysis',
            'current', '2024', 'recent', 'latest', 'specific', 'individual', 'particular'
        ]
        
        for indicator in specific_indicators:
            if indicator in title or indicator in snippet:
                specificity_score += 0.1
        
        # Negative indicators (decrease specificity)
        generic_indicators = [
            'homepage', 'home', 'index', 'main', 'general', 'overview', 'about us',
            'welcome', 'site map', 'contact', 'login', 'register'
        ]
        
        for indicator in generic_indicators:
            if indicator in url or indicator in title:
                specificity_score -= 0.2
        
        # URL structure analysis
        if len(url.split('/')) > 4:  # Deeper URLs are usually more specific
            specificity_score += 0.1
        
        if any(param in url for param in ['id=', 'listing=', 'profile=', 'page=']):
            specificity_score += 0.2
        
        return max(0.0, min(1.0, specificity_score))