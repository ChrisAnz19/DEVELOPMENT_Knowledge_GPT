#!/usr/bin/env python3
"""
Behavioral Context Query Generator.

This module generates search queries that focus on the behavioral context (what someone is looking for)
rather than generic role definitions. For example:
- Instead of "what is a human resources manager" 
- Generate "HR manager recruiting software evaluation"
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class BehavioralQuery:
    """Represents a behavioral-focused search query."""
    query: str
    behavioral_context: str
    role_context: str
    priority: int
    query_type: str  # 'behavioral', 'market', 'solution', 'trend'


class BehavioralContextQueryGenerator:
    """Generates queries focused on behavioral context rather than role definitions."""
    
    def __init__(self):
        # Behavioral action patterns to extract from prompts
        self.behavioral_patterns = {
            'evaluation': ['evaluating', 'comparing', 'assessing', 'reviewing', 'analyzing'],
            'research': ['researching', 'investigating', 'exploring', 'studying', 'looking into'],
            'purchasing': ['buying', 'purchasing', 'acquiring', 'investing in', 'shopping for'],
            'implementation': ['implementing', 'deploying', 'rolling out', 'adopting', 'installing'],
            'migration': ['migrating', 'switching', 'moving to', 'transitioning', 'upgrading'],
            'hiring': ['hiring', 'recruiting', 'looking for', 'seeking', 'staffing'],
            'expansion': ['expanding', 'scaling', 'growing', 'increasing', 'building']
        }
        
        # Role extraction patterns
        self.role_patterns = {
            'hr': ['hr', 'human resources', 'hr manager', 'hr director', 'people ops'],
            'marketing': ['marketing', 'cmo', 'marketing manager', 'marketing director'],
            'sales': ['sales', 'sales manager', 'sales director', 'business development'],
            'technology': ['cto', 'it', 'technology', 'tech manager', 'engineering'],
            'finance': ['cfo', 'finance', 'financial', 'accounting', 'controller'],
            'operations': ['operations', 'ops', 'operations manager', 'coo'],
            'executive': ['ceo', 'executive', 'c-suite', 'leadership', 'senior management']
        }
        
        # Solution categories for behavioral context
        self.solution_categories = {
            'hr': ['HRIS', 'payroll software', 'recruiting tools', 'performance management', 'employee engagement'],
            'marketing': ['marketing automation', 'CRM', 'email marketing', 'social media tools', 'analytics'],
            'sales': ['CRM', 'sales automation', 'lead generation', 'sales analytics', 'pipeline management'],
            'technology': ['cloud services', 'cybersecurity', 'development tools', 'infrastructure', 'SaaS platforms'],
            'finance': ['accounting software', 'financial planning', 'expense management', 'budgeting tools', 'ERP'],
            'operations': ['project management', 'workflow automation', 'supply chain', 'inventory management'],
            'executive': ['business intelligence', 'strategic planning', 'performance dashboards', 'analytics']
        }
    
    def generate_behavioral_queries(self, search_prompt: str, max_queries: int = 5) -> List[BehavioralQuery]:
        """
        Generate behavioral-focused queries from a search prompt.
        
        Args:
            search_prompt: Original search prompt (e.g., "find me HR managers looking for recruiting software")
            max_queries: Maximum number of queries to generate
            
        Returns:
            List of behavioral queries focused on what people are looking for, not role definitions
        """
        queries = []
        
        # Extract behavioral context and role from prompt
        behavioral_context = self._extract_behavioral_context(search_prompt)
        role_context = self._extract_role_context(search_prompt)
        
        if not behavioral_context:
            print(f"[Behavioral Query Generator] No behavioral context found in: {search_prompt}")
            return []
        
        print(f"[Behavioral Query Generator] Extracted - Role: {role_context}, Behavior: {behavioral_context}")
        
        # Generate different types of behavioral queries
        queries.extend(self._generate_solution_queries(role_context, behavioral_context))
        queries.extend(self._generate_market_trend_queries(role_context, behavioral_context))
        queries.extend(self._generate_industry_specific_queries(role_context, behavioral_context))
        queries.extend(self._generate_vendor_evaluation_queries(role_context, behavioral_context))
        
        # Sort by priority and limit
        queries.sort(key=lambda q: q.priority, reverse=True)
        return queries[:max_queries]
    
    def _extract_behavioral_context(self, prompt: str) -> Optional[str]:
        """Extract what someone is looking for (behavioral context) from the prompt."""
        prompt_lower = prompt.lower()
        
        # Look for explicit behavioral indicators
        for behavior_type, patterns in self.behavioral_patterns.items():
            for pattern in patterns:
                if pattern in prompt_lower:
                    # Extract the object of the behavior (what they're looking for)
                    return self._extract_behavior_object(prompt_lower, pattern)
        
        # Look for "looking for X" patterns
        looking_for_match = re.search(r'looking for\s+([^.]+)', prompt_lower)
        if looking_for_match:
            return looking_for_match.group(1).strip()
        
        # Look for "seeking X" patterns
        seeking_match = re.search(r'seeking\s+([^.]+)', prompt_lower)
        if seeking_match:
            return seeking_match.group(1).strip()
        
        # Look for "need X" patterns
        need_match = re.search(r'need\s+([^.]+)', prompt_lower)
        if need_match:
            return need_match.group(1).strip()
        
        return None
    
    def _extract_behavior_object(self, prompt: str, behavior_pattern: str) -> str:
        """Extract what someone is doing the behavior with/for."""
        # Find the behavior pattern and extract what follows
        pattern_index = prompt.find(behavior_pattern)
        if pattern_index == -1:
            return ""
        
        # Get text after the behavior pattern
        after_behavior = prompt[pattern_index + len(behavior_pattern):].strip()
        
        # Extract the first meaningful phrase (up to punctuation or conjunction)
        words = after_behavior.split()
        meaningful_words = []
        
        for word in words[:6]:  # Limit to first 6 words
            if word in ['and', 'or', 'but', 'for', 'to', 'in', 'on', 'at']:
                break
            meaningful_words.append(word)
        
        return ' '.join(meaningful_words).strip()
    
    def _extract_role_context(self, prompt: str) -> Optional[str]:
        """Extract role context from the prompt."""
        prompt_lower = prompt.lower()
        
        for role_category, patterns in self.role_patterns.items():
            for pattern in patterns:
                if pattern in prompt_lower:
                    return role_category
        
        return None
    
    def _generate_solution_queries(self, role: str, behavior: str) -> List[BehavioralQuery]:
        """Generate solution-focused queries."""
        queries = []
        
        if not role or not behavior:
            return queries
        
        # Get relevant solution categories for the role
        solutions = self.solution_categories.get(role, [])
        
        for solution in solutions[:3]:  # Limit to top 3 solutions
            # Check if the behavior is related to this solution
            if any(keyword in behavior.lower() for keyword in solution.lower().split()):
                query = f"{solution} {behavior} evaluation comparison"
                queries.append(BehavioralQuery(
                    query=query,
                    behavioral_context=behavior,
                    role_context=role,
                    priority=9,
                    query_type='solution'
                ))
        
        # Generic solution query
        if solutions:
            query = f"{role} {behavior} software solutions 2024"
            queries.append(BehavioralQuery(
                query=query,
                behavioral_context=behavior,
                role_context=role,
                priority=8,
                query_type='solution'
            ))
        
        return queries
    
    def _generate_market_trend_queries(self, role: str, behavior: str) -> List[BehavioralQuery]:
        """Generate market trend queries."""
        queries = []
        
        if not role or not behavior:
            return queries
        
        # Market trend query
        query = f"{role} {behavior} market trends 2024"
        queries.append(BehavioralQuery(
            query=query,
            behavioral_context=behavior,
            role_context=role,
            priority=7,
            query_type='market'
        ))
        
        # Industry analysis query
        query = f"{behavior} trends {role} industry analysis"
        queries.append(BehavioralQuery(
            query=query,
            behavioral_context=behavior,
            role_context=role,
            priority=6,
            query_type='trend'
        ))
        
        return queries
    
    def _generate_industry_specific_queries(self, role: str, behavior: str) -> List[BehavioralQuery]:
        """Generate industry-specific behavioral queries."""
        queries = []
        
        if not role or not behavior:
            return queries
        
        # Industry best practices
        query = f"{role} {behavior} best practices implementation"
        queries.append(BehavioralQuery(
            query=query,
            behavioral_context=behavior,
            role_context=role,
            priority=6,
            query_type='behavioral'
        ))
        
        # ROI and business case
        query = f"{behavior} ROI business case {role}"
        queries.append(BehavioralQuery(
            query=query,
            behavioral_context=behavior,
            role_context=role,
            priority=5,
            query_type='behavioral'
        ))
        
        return queries
    
    def _generate_vendor_evaluation_queries(self, role: str, behavior: str) -> List[BehavioralQuery]:
        """Generate vendor evaluation queries."""
        queries = []
        
        if not role or not behavior:
            return queries
        
        # Vendor comparison
        query = f"{behavior} vendor comparison {role} evaluation criteria"
        queries.append(BehavioralQuery(
            query=query,
            behavioral_context=behavior,
            role_context=role,
            priority=7,
            query_type='solution'
        ))
        
        # Implementation case studies
        query = f"{behavior} implementation case study {role}"
        queries.append(BehavioralQuery(
            query=query,
            behavioral_context=behavior,
            role_context=role,
            priority=6,
            query_type='behavioral'
        ))
        
        return queries


def test_behavioral_query_generator():
    """Test the behavioral context query generator."""
    
    print("Testing Behavioral Context Query Generator")
    print("=" * 45)
    
    generator = BehavioralContextQueryGenerator()
    
    # Test cases that should focus on behavioral context, not role definitions
    test_prompts = [
        "find me HR managers looking for recruiting software",
        "marketing directors evaluating CRM solutions", 
        "CTOs researching cybersecurity platforms",
        "CFOs seeking financial planning tools",
        "operations managers implementing workflow automation",
        "executives analyzing business intelligence solutions"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{i}. Prompt: {prompt}")
        queries = generator.generate_behavioral_queries(prompt, max_queries=3)
        
        print(f"   Generated {len(queries)} behavioral queries:")
        for j, query in enumerate(queries, 1):
            print(f"     {j}. {query.query}")
            print(f"        Type: {query.query_type} | Priority: {query.priority}")
            print(f"        Context: {query.role_context} → {query.behavioral_context}")
        
        # Check for generic role definition queries (should not exist)
        generic_violations = []
        for query in queries:
            query_lower = query.query.lower()
            if any(phrase in query_lower for phrase in ['what is', 'definition of', 'meaning of', 'explanation of']):
                generic_violations.append(query.query)
        
        if generic_violations:
            print(f"   ❌ VIOLATION: Found generic definition queries:")
            for violation in generic_violations:
                print(f"     - {violation}")
        else:
            print(f"   ✅ SUCCESS: All queries focus on behavioral context")


if __name__ == "__main__":
    test_behavioral_query_generator()