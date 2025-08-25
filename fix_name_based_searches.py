#!/usr/bin/env python3
"""
Fix for Name-Based Search Issue

This script identifies and fixes the critical issue where the evidence finder
is generating search queries based on prospect names, which returns irrelevant
websites that are just variations of the person's name instead of behavioral evidence.

PROBLEM: The system was generating queries like:
- "John Smith professional profile"
- "John Smith LinkedIn"
- "John Smith Company biography"

SOLUTION: Remove ALL name-based queries and focus ONLY on behavioral evidence.
"""

import re
from typing import List, Dict, Any


def identify_name_based_query_patterns():
    """Identify patterns that generate name-based queries."""
    
    problematic_patterns = [
        # Direct name inclusion patterns
        r'f[\'"].*{name}.*[\'"]',
        r'f[\'"].*\{candidate\.get\([\'"]name[\'"].*\}.*[\'"]',
        
        # Profile/biography patterns
        r'.*profile.*name.*',
        r'.*biography.*name.*',
        r'.*LinkedIn.*name.*',
        
        # Person-specific patterns
        r'person_queries.*=.*',
        r'individual_queries.*=.*',
        r'candidate_queries.*=.*'
    ]
    
    return problematic_patterns


def create_behavioral_only_queries(candidate: Dict[str, Any], search_context: str) -> List[str]:
    """
    Generate search queries that focus ONLY on behavioral evidence,
    never including the prospect's name.
    
    Args:
        candidate: Candidate information (name should be ignored)
        search_context: The behavioral search context
        
    Returns:
        List of behavioral-focused search queries
    """
    
    # Extract behavioral context WITHOUT using names
    title = candidate.get('title', '').lower()
    company = candidate.get('company', '').lower()
    
    # Generate role-based queries (no names)
    role_queries = []
    if title:
        # Focus on role transitions and behaviors
        role_queries.extend([
            f"{title} looking for new opportunities",
            f"{title} considering career change",
            f"{title} evaluating new roles",
            f"{title} job search activity",
            f"{title} career transition"
        ])
    
    # Generate company-context queries (no names)
    company_queries = []
    if company:
        company_queries.extend([
            f"executives leaving {company}",
            f"leadership changes at {company}",
            f"{company} employee departures",
            f"talent exodus from {company}"
        ])
    
    # Generate industry behavior queries
    industry_queries = []
    if 'startup' in search_context.lower():
        industry_queries.extend([
            f"{title} joining startups",
            f"executives moving to startups",
            f"corporate to startup transitions"
        ])
    
    if 'fortune 500' in search_context.lower():
        industry_queries.extend([
            f"{title} at fortune 500 companies",
            f"large company executive moves",
            f"corporate leadership changes"
        ])
    
    # Combine all behavioral queries (NO NAMES)
    all_queries = role_queries + company_queries + industry_queries
    
    # Filter out any queries that might accidentally include personal identifiers
    filtered_queries = []
    for query in all_queries:
        # Skip if query is too generic or might match names
        if len(query.split()) >= 3 and not _contains_potential_name(query):
            filtered_queries.append(query)
    
    return filtered_queries[:5]  # Limit to top 5 most relevant


def _contains_potential_name(query: str) -> bool:
    """Check if a query might contain a personal name."""
    
    # Common name patterns to avoid
    name_indicators = [
        r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # "John Smith" pattern
        r'\b[A-Z]\. [A-Z][a-z]+\b',      # "J. Smith" pattern
        r'\b[A-Z][a-z]+, [A-Z][a-z]+\b', # "Smith, John" pattern
    ]
    
    for pattern in name_indicators:
        if re.search(pattern, query):
            return True
    
    return False


def generate_safe_evidence_queries(behavioral_context: str, candidate_role: str = None, candidate_company: str = None) -> List[str]:
    """
    Generate evidence queries that are guaranteed to be name-free and behavior-focused.
    
    Args:
        behavioral_context: The behavioral search context (e.g., "CMO looking to leave Fortune 500 for startup")
        candidate_role: Optional role context (e.g., "Chief Marketing Officer")
        candidate_company: Optional company context (e.g., "Microsoft")
        
    Returns:
        List of safe, behavioral-focused search queries
    """
    
    queries = []
    
    # Extract behavioral intent from context
    behavioral_keywords = {
        'job_search': ['looking for', 'seeking', 'searching for', 'considering', 'evaluating'],
        'career_change': ['leaving', 'transitioning', 'moving from', 'switching', 'changing'],
        'company_type': ['startup', 'fortune 500', 'enterprise', 'small business', 'corporation'],
        'motivations': ['equity', 'growth', 'opportunity', 'challenge', 'innovation']
    }
    
    # Generate behavior-focused queries
    if candidate_role:
        role_clean = candidate_role.lower().replace('chief', '').replace('officer', '').strip()
        
        queries.extend([
            f"{role_clean} executive job market trends",
            f"{role_clean} leadership career transitions",
            f"{role_clean} role market analysis",
            f"senior {role_clean} hiring patterns"
        ])
    
    # Add company-context queries (without names)
    if candidate_company:
        queries.extend([
            f"executive departures {candidate_company}",
            f"leadership turnover {candidate_company}",
            f"talent retention {candidate_company}"
        ])
    
    # Add industry trend queries
    queries.extend([
        "executive job market trends 2024",
        "C-suite career transition patterns",
        "senior leadership hiring trends",
        "executive recruitment market analysis"
    ])
    
    # Filter and validate queries
    safe_queries = []
    for query in queries:
        if (len(query.split()) >= 3 and 
            not _contains_potential_name(query) and
            len(query) > 20):  # Ensure substantial queries
            safe_queries.append(query)
    
    return safe_queries[:6]  # Return top 6 most relevant


def validate_query_safety(query: str) -> Dict[str, Any]:
    """
    Validate that a query is safe and won't return name-based results.
    
    Args:
        query: Search query to validate
        
    Returns:
        Dict with validation results
    """
    
    issues = []
    
    # Check for potential names
    if _contains_potential_name(query):
        issues.append("Contains potential personal name pattern")
    
    # Check for profile/biography terms
    profile_terms = ['profile', 'biography', 'linkedin', 'about', 'personal']
    if any(term in query.lower() for term in profile_terms):
        issues.append("Contains profile/biography terms that may return personal pages")
    
    # Check for direct person references
    person_terms = ['person', 'individual', 'someone', 'he', 'she', 'his', 'her']
    if any(term in query.lower() for term in person_terms):
        issues.append("Contains direct person references")
    
    # Check query length and specificity
    if len(query.split()) < 3:
        issues.append("Query too short, may return generic results")
    
    if len(query) < 15:
        issues.append("Query too brief, lacks behavioral context")
    
    return {
        'is_safe': len(issues) == 0,
        'issues': issues,
        'query': query,
        'recommendation': 'SAFE' if len(issues) == 0 else 'UNSAFE - MODIFY OR REJECT'
    }


def test_query_safety():
    """Test the query safety validation."""
    
    test_queries = [
        # UNSAFE queries (should be rejected)
        '"John Smith" professional profile',
        '"Jane Doe" LinkedIn',
        'John Smith biography',
        'CEO profile',
        'executive personal information',
        
        # SAFE queries (should be approved)
        'CMO job market trends 2024',
        'executive career transition patterns',
        'Fortune 500 leadership changes',
        'startup executive hiring trends',
        'C-suite recruitment market analysis',
        'marketing executive job opportunities'
    ]
    
    print("Query Safety Validation Test")
    print("=" * 50)
    
    for query in test_queries:
        result = validate_query_safety(query)
        status = "✅ SAFE" if result['is_safe'] else "❌ UNSAFE"
        print(f"{status}: {query}")
        
        if not result['is_safe']:
            for issue in result['issues']:
                print(f"   - {issue}")
        print()


def create_behavioral_evidence_finder():
    """
    Create a new evidence finder that NEVER uses prospect names.
    """
    
    class BehavioralEvidenceFinder:
        """Evidence finder that focuses ONLY on behavioral patterns, never names."""
        
        def __init__(self):
            self.name_usage_blocked = True
            self.behavioral_focus_only = True
        
        def generate_evidence_queries(self, search_context: str, candidate_metadata: Dict[str, Any] = None) -> List[str]:
            """
            Generate evidence queries focused on behavioral patterns.
            
            CRITICAL: This method NEVER uses candidate names or personal identifiers.
            """
            
            # Extract role and company context (but never names)
            role = candidate_metadata.get('title', '') if candidate_metadata else ''
            company = candidate_metadata.get('company', '') if candidate_metadata else ''
            
            # Generate behavioral queries
            queries = generate_safe_evidence_queries(search_context, role, company)
            
            # Validate all queries for safety
            safe_queries = []
            for query in queries:
                validation = validate_query_safety(query)
                if validation['is_safe']:
                    safe_queries.append(query)
                else:
                    print(f"[BLOCKED UNSAFE QUERY]: {query}")
                    for issue in validation['issues']:
                        print(f"   - {issue}")
            
            return safe_queries
        
        def process_candidate_behavioral_evidence(self, candidate: Dict[str, Any], search_context: str) -> Dict[str, Any]:
            """
            Process candidate for behavioral evidence WITHOUT using their name.
            """
            
            # Generate safe queries
            evidence_queries = self.generate_evidence_queries(search_context, candidate)
            
            print(f"[Behavioral Evidence] Generated {len(evidence_queries)} name-free queries")
            for i, query in enumerate(evidence_queries, 1):
                print(f"   {i}. {query}")
            
            # Add evidence metadata
            candidate_copy = candidate.copy()
            candidate_copy['evidence_queries'] = evidence_queries
            candidate_copy['evidence_type'] = 'behavioral_only'
            candidate_copy['name_usage'] = 'blocked'
            
            return candidate_copy
    
    return BehavioralEvidenceFinder()


if __name__ == "__main__":
    print("Name-Based Search Fix Analysis")
    print("=" * 40)
    
    # Test query safety validation
    test_query_safety()
    
    # Test behavioral evidence finder
    print("\nTesting Behavioral Evidence Finder")
    print("=" * 40)
    
    finder = create_behavioral_evidence_finder()
    
    test_candidate = {
        'name': 'John Smith',  # This should NEVER be used in queries
        'title': 'Chief Marketing Officer',
        'company': 'Microsoft'
    }
    
    search_context = "CMO looking to leave Fortune 500 role for startup opportunity"
    
    result = finder.process_candidate_behavioral_evidence(test_candidate, search_context)
    
    print(f"\nResult for candidate (name hidden for privacy):")
    print(f"Evidence type: {result['evidence_type']}")
    print(f"Name usage: {result['name_usage']}")
    print(f"Generated queries: {len(result['evidence_queries'])}")
    
    # Verify no queries contain the name
    name_found = False
    for query in result['evidence_queries']:
        if 'john' in query.lower() or 'smith' in query.lower():
            name_found = True
            print(f"❌ CRITICAL ERROR: Query contains name: {query}")
    
    if not name_found:
        print("✅ SUCCESS: No queries contain prospect names!")
        print("   All queries focus on behavioral evidence only.")
    
    print(f"\nSample safe queries generated:")
    for i, query in enumerate(result['evidence_queries'][:3], 1):
        print(f"   {i}. {query}")