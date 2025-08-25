#!/usr/bin/env python3
"""
URL Evidence Finder - Main Orchestration Module.

This module coordinates the complete evidence gathering process by integrating
explanation analysis, search query generation, web search execution, and
evidence validation to find supporting URLs for candidate behavioral claims.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI

# Import our modules
from explanation_analyzer import ExplanationAnalyzer
from name_free_search_generator import NameFreeSearchGenerator
from web_search_engine import WebSearchEngine
from evidence_validator import EvidenceValidator
from evidence_models import (
    EvidenceURL, SearchableClaim, SearchResult,
    create_enhanced_candidate_response,
    validate_candidate_for_evidence_processing,
    extract_explanations_from_candidate,
    serialize_evidence_urls
)


class URLEvidenceFinder:
    """Main class that orchestrates the complete evidence gathering process."""
    
    def __init__(self, openai_client: Optional[OpenAI] = None):
        # Initialize components
        self.explanation_analyzer = ExplanationAnalyzer()
        self.query_generator = NameFreeSearchGenerator()
        self.web_search_engine = WebSearchEngine(openai_client)
        self.evidence_validator = EvidenceValidator()
        
        # Configuration
        self.max_claims_per_candidate = 5
        self.max_queries_per_claim = 3
        self.max_evidence_urls_per_candidate = 5
        self.enable_batch_optimization = True
        self.processing_timeout = 30  # seconds
        
        # Statistics
        self.stats = {
            'candidates_processed': 0,
            'claims_extracted': 0,
            'searches_executed': 0,
            'evidence_urls_found': 0,
            'processing_time_total': 0.0
        }
    
    async def find_evidence(
        self,
        explanations: List[str],
        candidate_context: Optional[Dict[str, Any]] = None
    ) -> List[EvidenceURL]:
        """
        Find evidence URLs for a single candidate's explanations.
        
        Args:
            explanations: List of behavioral explanations
            candidate_context: Optional candidate context (name, company, etc.)
            
        Returns:
            List of evidence URLs supporting the explanations
        """
        start_time = time.time()
        
        try:
            # Step 1: Extract searchable claims from explanations
            all_claims = []
            for explanation in explanations:
                claims = self.explanation_analyzer.extract_claims(explanation)
                all_claims.extend(claims)
            
            if not all_claims:
                print("[Evidence Finder] No searchable claims found in explanations")
                return []
            
            # Limit and prioritize claims
            prioritized_claims = sorted(all_claims, key=lambda c: (c.priority, c.confidence), reverse=True)
            selected_claims = prioritized_claims[:self.max_claims_per_candidate]
            
            print(f"[Evidence Finder] Processing {len(selected_claims)} claims from {len(explanations)} explanations")
            
            # Step 2: Generate search queries for each claim with diversity
            all_queries = []
            candidate_id = candidate_context.get('id', f'candidate_{int(time.time())}') if candidate_context else f'candidate_{int(time.time())}'
            
            for claim in selected_claims:
                queries = self.query_generator.generate_queries(claim, candidate_id)
                # Limit queries per claim
                limited_queries = queries[:self.max_queries_per_claim]
                all_queries.extend(limited_queries)
            
            if not all_queries:
                print("[Evidence Finder] No search queries generated")
                return []
            
            print(f"[Evidence Finder] Generated {len(all_queries)} search queries")
            
            # Step 3: Execute web searches
            search_results = await self.web_search_engine.search_for_evidence(all_queries)
            
            successful_searches = [r for r in search_results if r.success]
            print(f"[Evidence Finder] Completed {len(successful_searches)}/{len(search_results)} searches successfully")
            
            # Step 4: Validate and rank evidence URLs with uniqueness
            evidence_urls = []
            candidate_id = candidate_context.get('id', f'candidate_{int(time.time())}') if candidate_context else f'candidate_{int(time.time())}'
            
            for claim in selected_claims:
                # Find search results for this claim
                claim_results = [r for r in search_results if any(
                    term in r.query.query.lower() for term in claim.search_terms
                )]
                
                if claim_results:
                    claim_evidence = self.evidence_validator.validate_and_rank(claim_results, claim, candidate_id)
                    evidence_urls.extend(claim_evidence)
            
            # Remove duplicates and select final set
            final_evidence = self._select_final_evidence_set(evidence_urls)
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self.stats['candidates_processed'] += 1
            self.stats['claims_extracted'] += len(selected_claims)
            self.stats['searches_executed'] += len(search_results)
            self.stats['evidence_urls_found'] += len(final_evidence)
            self.stats['processing_time_total'] += processing_time
            
            print(f"[Evidence Finder] Found {len(final_evidence)} evidence URLs in {processing_time:.2f}s")
            
            return final_evidence
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"[Evidence Finder Error] Failed to find evidence: {str(e)}")
            return []
    
    async def process_candidate(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single candidate to add evidence URLs.
        
        Args:
            candidate: Candidate dictionary with explanations
            
        Returns:
            Enhanced candidate with evidence URLs
        """
        start_time = time.time()
        
        try:
            # Validate candidate
            if not validate_candidate_for_evidence_processing(candidate):
                print(f"[Evidence Finder] Invalid candidate format: {candidate.get('id', 'unknown')}")
                return self._create_failed_candidate_response(candidate, "Invalid candidate format")
            
            # Extract explanations
            explanations = extract_explanations_from_candidate(candidate)
            if not explanations:
                print(f"[Evidence Finder] No explanations found for candidate: {candidate.get('id', 'unknown')}")
                return self._create_empty_candidate_response(candidate)
            
            # Find evidence
            evidence_urls = await self.find_evidence(explanations, candidate)
            
            processing_time = time.time() - start_time
            
            # Create enhanced response
            enhanced_candidate = create_enhanced_candidate_response(
                candidate, evidence_urls, processing_time
            )
            
            return enhanced_candidate
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"[Evidence Finder Error] Failed to process candidate {candidate.get('id', 'unknown')}: {str(e)}")
            return self._create_failed_candidate_response(candidate, str(e), processing_time)
    
    async def process_candidates_batch(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple candidates efficiently with batch optimization.
        
        Args:
            candidates: List of candidate dictionaries
            
        Returns:
            List of enhanced candidates with evidence URLs
        """
        start_time = time.time()
        
        print(f"[Evidence Finder] Processing batch of {len(candidates)} candidates")
        
        if self.enable_batch_optimization:
            return await self._process_candidates_optimized(candidates)
        else:
            # Process candidates individually
            enhanced_candidates = []
            for candidate in candidates:
                enhanced = await self.process_candidate(candidate)
                enhanced_candidates.append(enhanced)
            
            batch_time = time.time() - start_time
            print(f"[Evidence Finder] Completed batch processing in {batch_time:.2f}s")
            
            return enhanced_candidates
    
    async def _process_candidates_optimized(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process candidates with batch optimization to reduce redundant searches."""
        start_time = time.time()
        
        # Step 1: Extract all claims from all candidates
        candidate_claims = {}
        all_unique_claims = {}
        
        for candidate in candidates:
            candidate_id = str(candidate.get('id', 'unknown'))
            
            if not validate_candidate_for_evidence_processing(candidate):
                candidate_claims[candidate_id] = []
                continue
            
            explanations = extract_explanations_from_candidate(candidate)
            claims = []
            
            for explanation in explanations:
                extracted_claims = self.explanation_analyzer.extract_claims(explanation)
                claims.extend(extracted_claims)
            
            # Prioritize and limit claims
            prioritized_claims = sorted(claims, key=lambda c: (c.priority, c.confidence), reverse=True)
            selected_claims = prioritized_claims[:self.max_claims_per_candidate]
            
            candidate_claims[candidate_id] = selected_claims
            
            # Add to unique claims (deduplicate similar claims)
            for claim in selected_claims:
                claim_key = self._generate_claim_key(claim)
                if claim_key not in all_unique_claims:
                    all_unique_claims[claim_key] = claim
        
        print(f"[Evidence Finder] Extracted {len(all_unique_claims)} unique claims from {len(candidates)} candidates")
        
        # Step 2: Generate queries for unique claims
        all_queries = []
        claim_to_queries = {}
        
        for claim_key, claim in all_unique_claims.items():
            queries = self.query_generator.generate_queries(claim)
            limited_queries = queries[:self.max_queries_per_claim]
            all_queries.extend(limited_queries)
            claim_to_queries[claim_key] = limited_queries
        
        print(f"[Evidence Finder] Generated {len(all_queries)} total queries")
        
        # Step 3: Execute all searches in batch
        search_results = await self.web_search_engine.search_for_evidence(all_queries)
        
        # Step 4: Process results for each candidate
        enhanced_candidates = []
        
        for candidate in candidates:
            candidate_id = str(candidate.get('id', 'unknown'))
            claims = candidate_claims.get(candidate_id, [])
            
            if not claims:
                enhanced_candidates.append(self._create_empty_candidate_response(candidate))
                continue
            
            # Find relevant search results for this candidate's claims
            candidate_evidence = []
            
            for claim in claims:
                claim_key = self._generate_claim_key(claim)
                claim_queries = claim_to_queries.get(claim_key, [])
                
                # Find search results for this claim's queries
                claim_results = []
                for query in claim_queries:
                    matching_results = [r for r in search_results if r.query.query == query.query]
                    claim_results.extend(matching_results)
                
                if claim_results:
                    claim_evidence = self.evidence_validator.validate_and_rank(claim_results, claim)
                    candidate_evidence.extend(claim_evidence)
            
            # Select final evidence set for this candidate
            final_evidence = self._select_final_evidence_set(candidate_evidence)
            
            # Create enhanced response
            processing_time = time.time() - start_time
            enhanced_candidate = create_enhanced_candidate_response(
                candidate, final_evidence, processing_time
            )
            enhanced_candidates.append(enhanced_candidate)
        
        batch_time = time.time() - start_time
        print(f"[Evidence Finder] Completed optimized batch processing in {batch_time:.2f}s")
        
        return enhanced_candidates
    
    def _generate_claim_key(self, claim: SearchableClaim) -> str:
        """Generate a key for claim deduplication."""
        # Use claim type and key search terms to create a unique key
        key_terms = sorted(claim.search_terms[:3])  # Use top 3 terms
        return f"{claim.claim_type.value}:{':'.join(key_terms)}"
    
    def _select_final_evidence_set(self, evidence_urls: List[EvidenceURL]) -> List[EvidenceURL]:
        """Select the final set of evidence URLs ensuring quality and diversity."""
        if not evidence_urls:
            return []
        
        # Remove duplicates
        seen_urls = set()
        unique_evidence = []
        for evidence in evidence_urls:
            if evidence.url not in seen_urls:
                seen_urls.add(evidence.url)
                unique_evidence.append(evidence)
        
        # Sort by combined score (relevance + quality)
        scored_evidence = sorted(
            unique_evidence,
            key=lambda e: (e.relevance_score * 0.6 + e.page_quality_score * 0.4),
            reverse=True
        )
        
        # Select diverse evidence types and domains
        final_evidence = []
        used_domains = set()
        used_evidence_types = set()
        
        # First pass: select high-quality diverse evidence
        for evidence in scored_evidence:
            if len(final_evidence) >= self.max_evidence_urls_per_candidate:
                break
            
            domain_new = evidence.url not in used_domains
            type_new = evidence.evidence_type not in used_evidence_types
            
            # Always include high-quality evidence, prefer diversity
            if evidence.confidence_level == "high" or domain_new or type_new or len(final_evidence) < 2:
                final_evidence.append(evidence)
                used_domains.add(evidence.url.split('/')[2] if '/' in evidence.url else evidence.url)
                used_evidence_types.add(evidence.evidence_type)
        
        # Fill remaining slots with best remaining evidence
        remaining_slots = self.max_evidence_urls_per_candidate - len(final_evidence)
        if remaining_slots > 0:
            remaining_evidence = [e for e in scored_evidence if e not in final_evidence]
            final_evidence.extend(remaining_evidence[:remaining_slots])
        
        return final_evidence
    
    def _create_empty_candidate_response(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Create response for candidate with no evidence found."""
        return create_enhanced_candidate_response(
            candidate,
            evidence_urls=[],
            processing_time=0.0
        )
    
    def _create_failed_candidate_response(
        self,
        candidate: Dict[str, Any],
        error_message: str,
        processing_time: float = 0.0
    ) -> Dict[str, Any]:
        """Create response for failed candidate processing."""
        enhanced_candidate = {
            **candidate,
            'evidence_urls': [],
            'evidence_summary': f"Evidence gathering failed: {error_message}",
            'evidence_confidence': 0.0,
            'evidence_processing_time': processing_time
        }
        return enhanced_candidate
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        avg_processing_time = (
            self.stats['processing_time_total'] / self.stats['candidates_processed']
            if self.stats['candidates_processed'] > 0 else 0.0
        )
        
        return {
            **self.stats,
            'average_processing_time': avg_processing_time,
            'average_evidence_per_candidate': (
                self.stats['evidence_urls_found'] / self.stats['candidates_processed']
                if self.stats['candidates_processed'] > 0 else 0.0
            )
        }
    
    def reset_statistics(self):
        """Reset processing statistics."""
        self.stats = {
            'candidates_processed': 0,
            'claims_extracted': 0,
            'searches_executed': 0,
            'evidence_urls_found': 0,
            'processing_time_total': 0.0
        }


async def test_url_evidence_finder():
    """Test function for the URL evidence finder."""
    # Create test candidates
    test_candidates = [
        {
            'id': '1',
            'name': 'John Doe',
            'title': 'VP of Sales',
            'company': 'TechCorp',
            'reasons': [
                'Currently researching Salesforce pricing options for enterprise deployment',
                'Actively comparing CRM solutions including HubSpot and Microsoft Dynamics'
            ]
        },
        {
            'id': '2',
            'name': 'Jane Smith',
            'title': 'Marketing Director',
            'company': 'StartupInc',
            'reasons': [
                'Investigating marketing automation platforms and their integration capabilities',
                'Analyzing competitor solutions in the customer support space'
            ]
        }
    ]
    
    print("Testing URL Evidence Finder:")
    print("=" * 60)
    
    # Initialize evidence finder
    evidence_finder = URLEvidenceFinder()
    
    # Test single candidate processing
    print("\n1. Testing single candidate processing:")
    enhanced_candidate = await evidence_finder.process_candidate(test_candidates[0])
    
    print(f"Candidate: {enhanced_candidate['name']}")
    print(f"Evidence URLs found: {len(enhanced_candidate.get('evidence_urls', []))}")
    print(f"Evidence summary: {enhanced_candidate.get('evidence_summary', 'N/A')}")
    print(f"Processing time: {enhanced_candidate.get('evidence_processing_time', 0):.2f}s")
    
    # Test batch processing
    print("\n2. Testing batch processing:")
    enhanced_candidates = await evidence_finder.process_candidates_batch(test_candidates)
    
    for candidate in enhanced_candidates:
        print(f"\nCandidate: {candidate['name']}")
        print(f"Evidence URLs: {len(candidate.get('evidence_urls', []))}")
        print(f"Summary: {candidate.get('evidence_summary', 'N/A')}")
    
    # Show statistics
    print("\n3. Processing Statistics:")
    stats = evidence_finder.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == '__main__':
    print("URL Evidence Finder module loaded successfully!")
    print("To test with actual API calls, run: asyncio.run(test_url_evidence_finder())")
    print("Make sure you have OPENAI_API_KEY environment variable set.")