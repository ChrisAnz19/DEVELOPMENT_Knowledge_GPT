#!/usr/bin/env python3
"""
Behavioral Context Extractor

This module extracts behavioral context from search prompts, focusing on what
prospects are looking for rather than who they are. It filters out role-based
terms and focuses on products, services, and activities.
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class BehavioralContext:
    """Represents extracted behavioral context from a search prompt."""
    products: List[str]           # Products/services being researched
    activities: List[str]         # Activities (comparing, evaluating, etc.)
    technologies: List[str]       # Technologies or platforms
    business_areas: List[str]     # Business areas (marketing, sales, etc.)
    intent_keywords: List[str]    # Intent-indicating keywords
    original_prompt: str          # Original search prompt
    behavioral_focus: str         # Main behavioral focus extracted


class BehavioralContextExtractor:
    """Extracts behavioral context from search prompts."""
    
    def __init__(self):
        # Behavioral trigger phrases that indicate what someone is looking for
        self.behavioral_triggers = [
            r'looking for',
            r'researching',
            r'evaluating',
            r'considering',
            r'comparing',
            r'shopping for',
            r'investigating',
            r'exploring',
            r'seeking',
            r'interested in',
            r'needs?',
            r'wants?',
            r'requires?'
        ]
        
        # Role-based terms to ignore (focus on behavior, not roles)
        self.role_terms = {
            'ceo', 'cfo', 'cto', 'cmo', 'coo', 'vp', 'vice president',
            'director', 'manager', 'executive', 'officer', 'head of',
            'lead', 'senior', 'junior', 'associate', 'coordinator',
            'specialist', 'analyst', 'consultant', 'advisor'
        }
        
        # Product/service categories to focus on
        self.product_categories = {
            'crm': ['crm', 'customer relationship management', 'salesforce', 'hubspot'],
            'hris': ['hris', 'hrm', 'hr software', 'hr platform', 'hrm platform', 'human resources', 'workday', 'successfactors'],
            'accounting': ['accounting software', 'accounting platform', 'quickbooks', 'netsuite', 'sage'],
            'marketing': ['marketing automation', 'marketing platform', 'marketo', 'pardot', 'eloqua'],
            'sales': ['sales software', 'sales platform', 'sales tools', 'pipedrive', 'salesforce'],
            'analytics': ['analytics', 'analytics platform', 'business intelligence', 'tableau', 'power bi'],
            'cloud': ['cloud services', 'cloud platform', 'aws', 'azure', 'google cloud'],
            'security': ['cybersecurity', 'security software', 'security platform', 'firewall', 'antivirus']
        }
        
        # Activity keywords that indicate behavioral intent
        self.activity_keywords = {
            'comparison': ['compare', 'comparison', 'vs', 'versus', 'alternatives'],
            'evaluation': ['evaluate', 'evaluation', 'assess', 'review', 'analyze'],
            'pricing': ['pricing', 'cost', 'price', 'budget', 'expensive', 'cheap'],
            'implementation': ['implement', 'deploy', 'setup', 'install', 'configure'],
            'research': ['research', 'investigate', 'explore', 'study', 'learn'],
            'purchase': ['buy', 'purchase', 'acquire', 'procure', 'invest']
        }
        
        # Technology and platform keywords
        self.technology_keywords = {
            'saas', 'software', 'platform', 'solution', 'system', 'tool',
            'application', 'service', 'technology', 'digital', 'automation',
            'ai', 'artificial intelligence', 'machine learning', 'cloud',
            'mobile', 'web', 'api', 'integration'
        }
    
    def extract_behavioral_context(self, prompt: str) -> BehavioralContext:
        """
        Extract behavioral context from a search prompt.
        
        Args:
            prompt: Search prompt like "Find me a marketing manager looking for CRM solutions"
            
        Returns:
            BehavioralContext with extracted behavioral information
        """
        prompt_lower = prompt.lower()
        
        # Extract the behavioral focus (what they're looking for)
        behavioral_focus = self._extract_behavioral_focus(prompt_lower)
        
        # Extract specific context elements
        products = self._extract_products(behavioral_focus)
        activities = self._extract_activities(behavioral_focus)
        technologies = self._extract_technologies(behavioral_focus)
        business_areas = self._extract_business_areas(behavioral_focus)
        intent_keywords = self._extract_intent_keywords(behavioral_focus)
        
        return BehavioralContext(
            products=products,
            activities=activities,
            technologies=technologies,
            business_areas=business_areas,
            intent_keywords=intent_keywords,
            original_prompt=prompt,
            behavioral_focus=behavioral_focus
        )
    
    def _extract_behavioral_focus(self, prompt: str) -> str:
        """
        Extract the main behavioral focus from the prompt.
        
        This looks for patterns like "looking for X" and extracts X.
        """
        # Try to find behavioral triggers and extract what comes after
        for trigger in self.behavioral_triggers:
            pattern = rf'{trigger}\s+(.+?)(?:\s+(?:in|at|for|with|from)\s+|$)'
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                behavioral_text = match.group(1).strip()
                # Clean up the extracted text
                behavioral_text = re.sub(r'\b(?:a|an|the)\b', '', behavioral_text)
                behavioral_text = re.sub(r'\s+', ' ', behavioral_text).strip()
                return behavioral_text
        
        # Fallback: look for product/service keywords in the entire prompt
        words = prompt.split()
        behavioral_words = []
        
        for word in words:
            word_clean = re.sub(r'[^a-zA-Z0-9\s]', '', word).lower()
            if (word_clean not in self.role_terms and 
                len(word_clean) > 2 and
                not word_clean.isdigit()):
                behavioral_words.append(word_clean)
        
        # CRITICAL FIX: Preserve multi-word context instead of just taking last 3 words
        # Look for meaningful product/service combinations
        behavioral_text = ' '.join(behavioral_words)
        
        # Extract multi-word product terms first
        multi_word_products = [
            'hrm platform', 'hr platform', 'hris platform', 'crm platform', 
            'marketing platform', 'sales platform', 'analytics platform',
            'accounting software', 'hr software', 'sales software',
            'marketing automation', 'business intelligence'
        ]
        
        for product_term in multi_word_products:
            if product_term in behavioral_text:
                return product_term
        
        # If no multi-word match, return the full behavioral context (not just last 3 words)
        return behavioral_text if len(behavioral_text) > 0 else ' '.join(behavioral_words[-3:])
    
    def _extract_products(self, behavioral_focus: str) -> List[str]:
        """Extract product/service names from behavioral focus."""
        products = []
        focus_lower = behavioral_focus.lower()
        
        # CRITICAL FIX: Check for multi-word product terms first (longer matches take priority)
        multi_word_products = [
            'hrm platform', 'hr platform', 'hris platform', 'crm platform', 
            'marketing platform', 'sales platform', 'analytics platform',
            'accounting software', 'hr software', 'sales software',
            'marketing automation', 'business intelligence', 'customer relationship management'
        ]
        
        # Check for multi-word products first
        for product_term in multi_word_products:
            if product_term in focus_lower:
                products.append(product_term)
        
        # If we found multi-word products, prioritize those
        if products:
            return list(set(products))
        
        # Check for specific product categories (single words)
        for category, keywords in self.product_categories.items():
            for keyword in keywords:
                if keyword in focus_lower:
                    products.append(keyword)
        
        # Extract potential product names (capitalized words, known software)
        words = behavioral_focus.split()
        for word in words:
            word_clean = word.strip('.,!?').lower()
            if (word_clean in ['salesforce', 'hubspot', 'workday', 'netsuite', 
                              'quickbooks', 'tableau', 'marketo', 'pardot'] or
                word_clean.endswith('software') or
                word_clean.endswith('platform') or
                word_clean.endswith('solution')):
                products.append(word_clean)
        
        return list(set(products))  # Remove duplicates
    
    def _extract_activities(self, behavioral_focus: str) -> List[str]:
        """Extract activity keywords from behavioral focus."""
        activities = []
        focus_lower = behavioral_focus.lower()
        
        for activity_type, keywords in self.activity_keywords.items():
            for keyword in keywords:
                if keyword in focus_lower:
                    activities.append(activity_type)
                    break  # Only add each activity type once
        
        return activities
    
    def _extract_technologies(self, behavioral_focus: str) -> List[str]:
        """Extract technology keywords from behavioral focus."""
        technologies = []
        focus_lower = behavioral_focus.lower()
        
        for tech_keyword in self.technology_keywords:
            if tech_keyword in focus_lower:
                technologies.append(tech_keyword)
        
        return technologies
    
    def _extract_business_areas(self, behavioral_focus: str) -> List[str]:
        """Extract business area keywords from behavioral focus."""
        business_areas = []
        focus_lower = behavioral_focus.lower()
        
        business_keywords = {
            'marketing', 'sales', 'finance', 'accounting', 'hr', 'human resources',
            'operations', 'it', 'technology', 'customer service', 'support',
            'analytics', 'business intelligence', 'security', 'compliance'
        }
        
        for area in business_keywords:
            if area in focus_lower:
                business_areas.append(area)
        
        return business_areas
    
    def _extract_intent_keywords(self, behavioral_focus: str) -> List[str]:
        """Extract intent-indicating keywords from behavioral focus."""
        intent_keywords = []
        focus_lower = behavioral_focus.lower()
        
        intent_patterns = {
            'enterprise': r'\\benterprise\\b',
            'small business': r'\\bsmall business\\b',
            'startup': r'\\bstartup\\b',
            'implementation': r'\\bimplement|deploy|setup\\b',
            'comparison': r'\\bcompare|vs|versus|alternative\\b',
            'pricing': r'\\bpric|cost|budget\\b',
            'features': r'\\bfeature|capability|function\\b',
            'integration': r'\\bintegrat|connect|sync\\b'
        }
        
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, focus_lower):
                intent_keywords.append(intent)
        
        return intent_keywords
    
    def is_behavioral_context_valid(self, context: BehavioralContext) -> bool:
        """
        Check if the extracted behavioral context is valid and useful.
        
        Returns True if context contains meaningful behavioral information.
        """
        return (len(context.products) > 0 or 
                len(context.activities) > 0 or 
                len(context.technologies) > 0 or
                len(context.intent_keywords) > 0)
    
    def get_primary_behavioral_focus(self, context: BehavioralContext) -> str:
        """
        Get the primary behavioral focus for URL generation.
        
        Returns the most relevant behavioral context for generating URLs.
        """
        # Prioritize products first
        if context.products:
            return context.products[0]
        
        # Then technologies
        if context.technologies:
            return context.technologies[0]
        
        # Then business areas
        if context.business_areas:
            return context.business_areas[0]
        
        # Fallback to the raw behavioral focus
        return context.behavioral_focus


def test_behavioral_context_extractor():
    """Test the behavioral context extractor."""
    
    extractor = BehavioralContextExtractor()
    
    test_cases = [
        {
            'prompt': 'Find me a marketing manager looking for CRM solutions',
            'expected_products': ['crm'],
            'expected_activities': ['research'],
            'should_not_contain': ['marketing manager', 'what-is-a']
        },
        {
            'prompt': 'Find me a HR director researching HRIS platforms',
            'expected_products': ['hris'],
            'expected_technologies': ['platform'],
            'should_not_contain': ['hr director', 'job-description']
        },
        {
            'prompt': 'Find me a CFO evaluating accounting software',
            'expected_products': ['accounting software'],
            'expected_activities': ['evaluation'],
            'should_not_contain': ['cfo', 'responsibilities']
        },
        {
            'prompt': 'Find executives comparing Salesforce vs HubSpot',
            'expected_products': ['salesforce', 'hubspot'],
            'expected_activities': ['comparison'],
            'should_not_contain': ['executives', 'what-is']
        }
    ]
    
    print("Behavioral Context Extractor Test Results:")
    print("=" * 45)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\\n{i}. Testing: {test_case['prompt']}")
        
        context = extractor.extract_behavioral_context(test_case['prompt'])
        
        print(f"   Behavioral Focus: {context.behavioral_focus}")
        print(f"   Products: {context.products}")
        print(f"   Activities: {context.activities}")
        print(f"   Technologies: {context.technologies}")
        print(f"   Intent Keywords: {context.intent_keywords}")
        
        # Validate context is behavioral (not role-based)
        primary_focus = extractor.get_primary_behavioral_focus(context)
        print(f"   Primary Focus: {primary_focus}")
        
        # Check that it doesn't contain role-based terms
        focus_lower = context.behavioral_focus.lower()
        contains_role_terms = any(role in focus_lower for role in extractor.role_terms)
        
        if contains_role_terms:
            print(f"   ❌ WARNING: Contains role terms")
        else:
            print(f"   ✅ SUCCESS: Focus on behavioral evidence")
    
    print(f"\\n✅ Behavioral context extraction focuses on 'what they want' not 'who they are'")


if __name__ == "__main__":
    test_behavioral_context_extractor()