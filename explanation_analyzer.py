#!/usr/bin/env python3
"""
Explanation Analysis Engine for URL Evidence Finder.

This module analyzes candidate behavioral explanations to extract searchable claims,
identify entities (companies, products, activities), and categorize claim types
for targeted evidence gathering.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ClaimType(Enum):
    """Types of behavioral claims that can be extracted."""
    COMPANY_RESEARCH = "company_research"
    PRODUCT_EVALUATION = "product_evaluation"
    PRICING_RESEARCH = "pricing_research"
    FEATURE_COMPARISON = "feature_comparison"
    VENDOR_EVALUATION = "vendor_evaluation"
    MARKET_RESEARCH = "market_research"
    REAL_ESTATE_RESEARCH = "real_estate_research"
    FINANCIAL_SERVICES_RESEARCH = "financial_services_research"
    INVESTMENT_RESEARCH = "investment_research"
    GENERAL_ACTIVITY = "general_activity"


@dataclass
class SearchableClaim:
    """Represents a claim extracted from behavioral explanations."""
    text: str                           # Original claim text
    entities: Dict[str, List[str]]      # Extracted entities (companies, products, activities)
    claim_type: ClaimType               # Categorized claim type
    priority: int                       # Search priority (1-10, 10 being highest)
    search_terms: List[str]             # Key terms for searching
    confidence: float                   # Confidence in claim extraction (0-1)


class ExplanationAnalyzer:
    """Analyzes behavioral explanations to extract searchable claims."""
    
    def __init__(self):
        # Company name patterns (major SaaS/tech companies)
        self.company_patterns = [
            r'\b(Salesforce|HubSpot|Microsoft|Google|Amazon|Oracle|SAP|Adobe|Zoom|Slack)\b',
            r'\b(Shopify|Stripe|Twilio|Zendesk|Atlassian|ServiceNow|Workday|Okta)\b',
            r'\b(Tableau|Snowflake|Databricks|MongoDB|Redis|Elastic|Splunk)\b',
            r'\b(DocuSign|Box|Dropbox|Asana|Trello|Monday\.com|Notion)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+(?:Inc|Corp|LLC|Ltd|Company|Technologies|Software|Solutions))\b',
        ]
        
        # Product/service patterns
        self.product_patterns = [
            # Tech/Software
            r'\b(CRM|ERP|SaaS|API|SDK|platform|software|tool|solution|service|system)\b',
            r'\b(automation|analytics|dashboard|integration|workflow|pipeline)\b',
            r'\b(marketing|sales|customer|support|finance|HR|accounting)\b',
            # Real Estate
            r'\b(real\s+estate|property|properties|listing|listings|home|homes|house|houses|mansion|mansions|estate|residential|luxury\s+home)\b',
            r'\b(MLS|realtor|realty|brokerage|agent|broker|investment\s+property|rental|commercial\s+real\s+estate)\b',
            # Financial Services
            r'\b(mortgage|loan|lending|financing|calculator|rate|rates|banking|financial|investment|portfolio)\b',
            r'\b(pre-approval|refinancing|credit|debt|wealth\s+management|financial\s+planning)\b',
            # Investment & Forums
            r'\b(investment|investing|investor|forum|forums|community|discussion|networking|club)\b',
        ]
        
        # Activity patterns (research behaviors)
        self.activity_patterns = [
            r'\b(research(?:ed|ing)?|investigat(?:ed|ing)?|analyz(?:ed|ing)?|compar(?:ed|ing)?|evaluat(?:ed|ing)?|review(?:ed|ing)?)\b',
            r'\b(visit(?:ed|ing)?|brows(?:ed|ing)?|explor(?:ed|ing)?|check(?:ed|ing)?|look(?:ed|ing)\s+(?:at|into))\b',
            r'\b(read(?:ing)?|stud(?:ied|ying)?|examin(?:ed|ing)?|assess(?:ed|ing)?|consider(?:ed|ing)?)\b',
            r'\b(download(?:ed|ing)?|request(?:ed|ing)?|demo|trial|consultation|meeting)\b',
            # Real estate specific activities
            r'\b(saved|favorited|shared|contacted|toured|viewed|scheduled)\b',
            r'\b(engaged\s+with|interacted\s+with|used|accessed|joined)\b',
        ]
        
        # Pricing/cost patterns
        self.pricing_patterns = [
            r'\b(pric(?:ing|e)|cost|plan|subscription|fee|rate|budget|expense)\b',
            r'\b(quote|proposal|estimate|ROI|value|investment)\b',
        ]
        
        # Feature/comparison patterns
        self.feature_patterns = [
            r'\b(feature|functionality|capability|benefit|advantage|comparison)\b',
            r'\b(vs|versus|against|alternative|competitor|option)\b',
        ]
        
        # Industry/market patterns
        self.industry_patterns = [
            r'\b(market\s+trend|industry\s+analysis|competitive\s+landscape|market\s+research)\b',
            r'\b(digital\s+transformation|automation|AI|machine\s+learning|cloud)\b',
            r'\b(B2B|SaaS|enterprise|startup|technology|fintech|healthtech)\b',
        ]
    
    def extract_claims(self, explanation: str) -> List[SearchableClaim]:
        """
        Extract searchable claims from behavioral explanations.
        
        Args:
            explanation: Behavioral insight text
            
        Returns:
            List of searchable claims with entities and context
        """
        if not explanation or not explanation.strip():
            return []
        
        claims = []
        
        # Split explanation into sentences for individual analysis
        sentences = self._split_into_sentences(explanation)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue
            
            # Check if sentence contains searchable content
            if self._is_searchable_sentence(sentence):
                claim = self._create_searchable_claim(sentence, explanation)
                if claim:
                    claims.append(claim)
        
        # If no individual sentences were searchable, try the whole explanation
        if not claims and self._is_searchable_sentence(explanation):
            claim = self._create_searchable_claim(explanation, explanation)
            if claim:
                claims.append(claim)
        
        # Sort by priority and confidence
        claims.sort(key=lambda c: (c.priority, c.confidence), reverse=True)
        
        # Limit to top 5 claims per explanation
        return claims[:5]
    
    def identify_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract companies, products, and activities from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with entity types and extracted values
        """
        entities = {
            'companies': [],
            'products': [],
            'activities': [],
            'pricing_terms': [],
            'features': []
        }
        
        # Extract companies
        for pattern in self.company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['companies'].extend([match.strip() for match in matches if match.strip()])
        
        # Extract products/services
        for pattern in self.product_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['products'].extend([match.strip() for match in matches if match.strip()])
        
        # Extract activities
        for pattern in self.activity_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['activities'].extend([match.strip() for match in matches if match.strip()])
        
        # Extract pricing terms
        for pattern in self.pricing_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['pricing_terms'].extend([match.strip() for match in matches if match.strip()])
        
        # Extract feature terms
        for pattern in self.feature_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['features'].extend([match.strip() for match in matches if match.strip()])
        
        # Remove duplicates and clean up
        for key in entities:
            entities[key] = list(set([entity.lower() for entity in entities[key] if entity]))
        
        return entities
    
    def categorize_claim(self, claim: str) -> ClaimType:
        """
        Categorize claim type based on content analysis.
        
        Args:
            claim: The claim text to categorize
            
        Returns:
            ClaimType enum value
        """
        claim_lower = claim.lower()
        
        # Check for real estate research (highest priority for real estate terms)
        real_estate_terms = [
            'real estate', 'property', 'properties', 'listing', 'listings', 
            'home', 'homes', 'house', 'houses', 'mansion', 'mansions', 
            'estate', 'residential', 'luxury home', 'greenwich', 'westchester',
            'mls', 'realtor', 'realty', 'brokerage', 'agent', 'broker'
        ]
        if any(term in claim_lower for term in real_estate_terms):
            return ClaimType.REAL_ESTATE_RESEARCH
        
        # Check for financial services research
        financial_terms = [
            'mortgage', 'loan', 'lending', 'financing', 'calculator', 
            'rate', 'rates', 'banking', 'financial', 'pre-approval', 
            'refinancing', 'credit', 'debt', 'wealth management'
        ]
        if any(term in claim_lower for term in financial_terms):
            return ClaimType.FINANCIAL_SERVICES_RESEARCH
        
        # Check for investment research
        investment_terms = [
            'investment', 'investing', 'investor', 'forum', 'forums', 
            'community', 'discussion', 'networking', 'club', 'portfolio'
        ]
        if any(term in claim_lower for term in investment_terms):
            return ClaimType.INVESTMENT_RESEARCH
        
        # Check for pricing research
        if any(re.search(pattern, claim, re.IGNORECASE) for pattern in self.pricing_patterns):
            return ClaimType.PRICING_RESEARCH
        
        # Check for feature comparison
        if any(re.search(pattern, claim, re.IGNORECASE) for pattern in self.feature_patterns):
            return ClaimType.FEATURE_COMPARISON
        
        # Check for company-specific research
        company_mentioned = any(re.search(pattern, claim, re.IGNORECASE) for pattern in self.company_patterns)
        if company_mentioned:
            if any(word in claim_lower for word in ['product', 'solution', 'platform', 'tool']):
                return ClaimType.PRODUCT_EVALUATION
            elif any(word in claim_lower for word in ['vendor', 'provider', 'supplier']):
                return ClaimType.VENDOR_EVALUATION
            else:
                return ClaimType.COMPANY_RESEARCH
        
        # Check for market/industry research
        if any(re.search(pattern, claim, re.IGNORECASE) for pattern in self.industry_patterns):
            return ClaimType.MARKET_RESEARCH
        
        # Check for product evaluation
        if any(re.search(pattern, claim, re.IGNORECASE) for pattern in self.product_patterns):
            return ClaimType.PRODUCT_EVALUATION
        
        # Default to general activity
        return ClaimType.GENERAL_ACTIVITY
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting on common punctuation
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _is_searchable_sentence(self, sentence: str) -> bool:
        """Check if a sentence contains searchable content."""
        sentence_lower = sentence.lower()
        
        # Must contain some form of research/activity behavior
        has_activity = any(
            re.search(pattern, sentence, re.IGNORECASE) 
            for pattern in self.activity_patterns
        )
        
        # Must mention something specific (company, product, or concept)
        has_entity = (
            any(re.search(pattern, sentence, re.IGNORECASE) for pattern in self.company_patterns) or
            any(re.search(pattern, sentence, re.IGNORECASE) for pattern in self.product_patterns) or
            any(re.search(pattern, sentence, re.IGNORECASE) for pattern in self.pricing_patterns) or
            any(re.search(pattern, sentence, re.IGNORECASE) for pattern in self.feature_patterns)
        )
        
        # Should be substantial enough (more than 5 words)
        has_substance = len(sentence.split()) > 5
        
        return has_activity and has_entity and has_substance
    
    def _create_searchable_claim(self, claim_text: str, full_explanation: str) -> Optional[SearchableClaim]:
        """Create a SearchableClaim object from claim text."""
        try:
            # Extract entities
            entities = self.identify_entities(claim_text)
            
            # Categorize claim
            claim_type = self.categorize_claim(claim_text)
            
            # Generate search terms
            search_terms = self._generate_search_terms(claim_text, entities)
            
            # Calculate priority
            priority = self._calculate_priority(claim_text, entities, claim_type)
            
            # Calculate confidence
            confidence = self._calculate_confidence(claim_text, entities)
            
            return SearchableClaim(
                text=claim_text,
                entities=entities,
                claim_type=claim_type,
                priority=priority,
                search_terms=search_terms,
                confidence=confidence
            )
        
        except Exception as e:
            print(f"[Explanation Analyzer] Error creating claim: {e}")
            return None
    
    def _generate_search_terms(self, claim_text: str, entities: Dict[str, List[str]]) -> List[str]:
        """Generate key search terms from claim and entities."""
        search_terms = []
        
        # Add company names (highest priority)
        search_terms.extend(entities.get('companies', []))
        
        # Add product terms
        search_terms.extend(entities.get('products', []))
        
        # Add pricing terms if relevant
        if entities.get('pricing_terms'):
            search_terms.extend(entities.get('pricing_terms', []))
        
        # Add feature terms if relevant
        if entities.get('features'):
            search_terms.extend(entities.get('features', []))
        
        # Extract additional key terms from claim text
        claim_words = claim_text.lower().split()
        key_words = [word for word in claim_words if len(word) > 3 and word not in ['that', 'this', 'with', 'from', 'they', 'have', 'been']]
        search_terms.extend(key_words[:3])  # Add top 3 key words
        
        # Remove duplicates and limit
        search_terms = list(set([term for term in search_terms if term]))
        return search_terms[:8]  # Limit to 8 terms
    
    def _calculate_priority(self, claim_text: str, entities: Dict[str, List[str]], claim_type: ClaimType) -> int:
        """Calculate search priority for a claim (1-10, 10 being highest)."""
        priority = 5  # Base priority
        
        # Higher priority for specific claim types
        if claim_type in [ClaimType.PRICING_RESEARCH, ClaimType.COMPANY_RESEARCH]:
            priority += 2
        elif claim_type in [ClaimType.PRODUCT_EVALUATION, ClaimType.FEATURE_COMPARISON]:
            priority += 1
        
        # Higher priority for specific company mentions
        if entities.get('companies'):
            priority += 2
        
        # Higher priority for pricing-related claims
        if entities.get('pricing_terms'):
            priority += 1
        
        # Lower priority for very general claims
        if claim_type == ClaimType.GENERAL_ACTIVITY and not entities.get('companies'):
            priority -= 2
        
        # Ensure priority is within bounds
        return max(1, min(10, priority))
    
    def _calculate_confidence(self, claim_text: str, entities: Dict[str, List[str]]) -> float:
        """Calculate confidence in claim extraction (0-1)."""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for specific entities
        if entities.get('companies'):
            confidence += 0.2
        
        if entities.get('products'):
            confidence += 0.1
        
        if entities.get('pricing_terms'):
            confidence += 0.1
        
        # Higher confidence for longer, more detailed claims
        word_count = len(claim_text.split())
        if word_count > 10:
            confidence += 0.1
        elif word_count > 15:
            confidence += 0.2
        
        # Lower confidence for very general claims
        if not any(entities.values()):
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))


def test_explanation_analyzer():
    """Test function for the explanation analyzer."""
    analyzer = ExplanationAnalyzer()
    
    # Test explanations
    test_explanations = [
        "Visited luxury real estate websites for Greenwich, Connecticut multiple times in the past month",
        "Engaged with financial calculators and mortgage rate comparison tools on real estate platforms",
        "Joined exclusive real estate investment forums discussing properties in Greenwich",
        "Currently researching Salesforce pricing options for enterprise deployment",
        "Actively comparing CRM solutions including HubSpot and Microsoft Dynamics",
        "Downloaded mortgage pre-approval applications from multiple lenders",
        "Saved multiple luxury home listings to favorites and shared them with a real estate agent"
    ]
    
    print("Testing Explanation Analyzer:")
    print("=" * 50)
    
    for i, explanation in enumerate(test_explanations, 1):
        print(f"\n{i}. Explanation: {explanation}")
        claims = analyzer.extract_claims(explanation)
        
        for j, claim in enumerate(claims, 1):
            print(f"   Claim {j}:")
            print(f"     Text: {claim.text}")
            print(f"     Type: {claim.claim_type.value}")
            print(f"     Entities: {claim.entities}")
            print(f"     Search Terms: {claim.search_terms}")
            print(f"     Priority: {claim.priority}")
            print(f"     Confidence: {claim.confidence:.2f}")


if __name__ == '__main__':
    test_explanation_analyzer()