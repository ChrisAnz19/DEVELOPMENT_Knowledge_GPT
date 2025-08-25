#!/usr/bin/env python3
"""
Evidence Integration Module for URL Evidence Finder.

This module integrates the URL Evidence Finder with the existing candidate
processing pipeline, adding evidence URLs to search results while maintaining
backward compatibility.
"""

import asyncio
import time
import os
from typing import List, Dict, Any, Optional
from openai import OpenAI

# Import evidence finder components
from url_evidence_finder import URLEvidenceFinder
from evidence_cache import OptimizedEvidenceFinder
from evidence_models import (
    validate_candidate_for_evidence_processing,
    extract_explanations_from_candidate,
    create_enhanced_candidate_response
)


class EvidenceIntegrationConfig:
    """Configuration for evidence integration."""
    
    def __init__(self):
        # Feature flags
        self.enabled = os.getenv('EVIDENCE_FINDER_ENABLED', 'true').lower() == 'true'
        self.use_caching = os.getenv('EVIDENCE_FINDER_CACHE', 'true').lower() == 'true'
        self.async_processing = os.getenv('EVIDENCE_FINDER_ASYNC', 'true').lower() == 'true'
        
        # Performance settings
        self.max_candidates_for_evidence = int(os.getenv('EVIDENCE_MAX_CANDIDATES', '10'))
        self.processing_timeout = int(os.getenv('EVIDENCE_TIMEOUT', '30'))
        self.cache_size = int(os.getenv('EVIDENCE_CACHE_SIZE', '1000'))
        
        # Quality settings
        self.min_explanation_length = int(os.getenv('EVIDENCE_MIN_EXPLANATION_LENGTH', '10'))
        self.require_behavioral_data = os.getenv('EVIDENCE_REQUIRE_BEHAVIORAL', 'false').lower() == 'true'
        
        print(f"[Evidence Integration] Configuration loaded - Enabled: {self.enabled}, Caching: {self.use_caching}")


class EvidenceIntegrationService:
    """Service that integrates evidence finding with the existing pipeline."""
    
    def __init__(self, openai_client: Optional[OpenAI] = None):
        self.config = EvidenceIntegrationConfig()
        
        if self.config.enabled:
            # Initialize evidence finder
            base_finder = URLEvidenceFinder(openai_client)
            
            if self.config.use_caching:
                self.evidence_finder = OptimizedEvidenceFinder(base_finder, self.config.cache_size)
            else:
                self.evidence_finder = base_finder
            
            print(f"[Evidence Integration] Service initialized with {'caching' if self.config.use_caching else 'no caching'}")
        else:
            self.evidence_finder = None
            print("[Evidence Integration] Service disabled via configuration")
        
        # Statistics
        self.stats = {
            'candidates_processed': 0,
            'evidence_found': 0,
            'processing_time_total': 0.0,
            'errors': 0
        }
    
    async def enhance_candidates_with_evidence(
        self,
        candidates: List[Dict[str, Any]],
        search_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Enhance candidates with evidence URLs.
        
        Args:
            candidates: List of candidate dictionaries
            search_prompt: Original search prompt for context
            
        Returns:
            Enhanced candidates with evidence URLs (or original if disabled/failed)
        """
        if not self.config.enabled or not self.evidence_finder:
            print("[Evidence Integration] Evidence finding disabled, returning original candidates")
            return candidates
        
        if not candidates:
            return candidates
        
        start_time = time.time()
        
        try:
            # Filter candidates that are suitable for evidence processing
            eligible_candidates = self._filter_eligible_candidates(candidates)
            
            if not eligible_candidates:
                print("[Evidence Integration] No eligible candidates for evidence processing")
                return candidates
            
            # Limit candidates to avoid excessive processing
            limited_candidates = eligible_candidates[:self.config.max_candidates_for_evidence]
            
            print(f"[Evidence Integration] Processing {len(limited_candidates)} candidates for evidence URLs")
            
            # Process candidates with evidence finding
            if self.config.async_processing:
                enhanced_candidates = await self._process_candidates_async(limited_candidates)
            else:
                enhanced_candidates = await self._process_candidates_sequential(limited_candidates)
            
            # Merge enhanced candidates back with original list
            enhanced_results = self._merge_enhanced_candidates(candidates, enhanced_candidates)
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self.stats['candidates_processed'] += len(limited_candidates)
            self.stats['evidence_found'] += sum(
                len(c.get('evidence_urls', [])) for c in enhanced_candidates
            )
            self.stats['processing_time_total'] += processing_time
            
            print(f"[Evidence Integration] Completed in {processing_time:.2f}s")
            
            return enhanced_results
            
        except Exception as e:
            self.stats['errors'] += 1
            processing_time = time.time() - start_time
            print(f"[Evidence Integration Error] Failed to enhance candidates: {str(e)} (took {processing_time:.2f}s)")
            
            # Return original candidates on error to maintain functionality
            return candidates
    
    def _filter_eligible_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter candidates that are eligible for evidence processing."""
        eligible = []
        
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            
            # Check if candidate has required fields
            if not validate_candidate_for_evidence_processing(candidate):
                continue
            
            # Extract explanations to check quality
            explanations = extract_explanations_from_candidate(candidate)
            
            # Filter by explanation quality
            valid_explanations = [
                exp for exp in explanations 
                if len(exp.strip()) >= self.config.min_explanation_length
            ]
            
            if not valid_explanations:
                continue
            
            # Check for behavioral data if required
            if self.config.require_behavioral_data:
                behavioral_data = candidate.get('behavioral_data', {})
                if not behavioral_data or not isinstance(behavioral_data, dict):
                    continue
            
            eligible.append(candidate)
        
        return eligible
    
    async def _process_candidates_async(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process candidates asynchronously with timeout."""
        try:
            # Use the evidence finder's batch processing
            if hasattr(self.evidence_finder, 'process_candidates_optimized'):
                enhanced_candidates = await asyncio.wait_for(
                    self.evidence_finder.process_candidates_optimized(candidates),
                    timeout=self.config.processing_timeout
                )
            else:
                enhanced_candidates = await asyncio.wait_for(
                    self.evidence_finder.base_finder.process_candidates_batch(candidates),
                    timeout=self.config.processing_timeout
                )
            
            return enhanced_candidates
            
        except asyncio.TimeoutError:
            print(f"[Evidence Integration] Processing timed out after {self.config.processing_timeout}s")
            return self._create_timeout_responses(candidates)
        
        except Exception as e:
            print(f"[Evidence Integration] Async processing failed: {str(e)}")
            return self._create_error_responses(candidates, str(e))
    
    async def _process_candidates_sequential(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process candidates sequentially."""
        enhanced_candidates = []
        
        for candidate in candidates:
            try:
                if hasattr(self.evidence_finder, 'base_finder'):
                    enhanced = await self.evidence_finder.base_finder.process_candidate(candidate)
                else:
                    enhanced = await self.evidence_finder.process_candidate(candidate)
                
                enhanced_candidates.append(enhanced)
                
            except Exception as e:
                print(f"[Evidence Integration] Failed to process candidate {candidate.get('id', 'unknown')}: {str(e)}")
                # Add candidate with empty evidence on error
                enhanced_candidates.append(self._create_error_response(candidate, str(e)))
        
        return enhanced_candidates
    
    def _merge_enhanced_candidates(
        self,
        original_candidates: List[Dict[str, Any]],
        enhanced_candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge enhanced candidates back with the original list."""
        # Create a mapping of enhanced candidates by ID
        enhanced_map = {}
        for enhanced in enhanced_candidates:
            candidate_id = str(enhanced.get('id', ''))
            if candidate_id:
                enhanced_map[candidate_id] = enhanced
        
        # Merge enhanced data back into original list
        merged_candidates = []
        for original in original_candidates:
            candidate_id = str(original.get('id', ''))
            
            if candidate_id in enhanced_map:
                # Use enhanced version
                enhanced = enhanced_map[candidate_id]
                merged_candidates.append(enhanced)
            else:
                # Use original version (no evidence processing)
                merged_candidates.append(original)
        
        return merged_candidates
    
    def _create_timeout_responses(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create timeout responses for candidates."""
        return [
            {
                **candidate,
                'evidence_urls': [],
                'evidence_summary': 'Evidence gathering timed out',
                'evidence_confidence': 0.0,
                'evidence_processing_time': self.config.processing_timeout
            }
            for candidate in candidates
        ]
    
    def _create_error_responses(self, candidates: List[Dict[str, Any]], error_message: str) -> List[Dict[str, Any]]:
        """Create error responses for candidates."""
        return [
            self._create_error_response(candidate, error_message)
            for candidate in candidates
        ]
    
    def _create_error_response(self, candidate: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """Create error response for a single candidate."""
        return {
            **candidate,
            'evidence_urls': [],
            'evidence_summary': f'Evidence gathering failed: {error_message}',
            'evidence_confidence': 0.0,
            'evidence_processing_time': 0.0
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get integration statistics."""
        avg_processing_time = (
            self.stats['processing_time_total'] / self.stats['candidates_processed']
            if self.stats['candidates_processed'] > 0 else 0.0
        )
        
        return {
            **self.stats,
            'average_processing_time': avg_processing_time,
            'average_evidence_per_candidate': (
                self.stats['evidence_found'] / self.stats['candidates_processed']
                if self.stats['candidates_processed'] > 0 else 0.0
            ),
            'success_rate': (
                (self.stats['candidates_processed'] - self.stats['errors']) / self.stats['candidates_processed']
                if self.stats['candidates_processed'] > 0 else 0.0
            )
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        base_stats = self.get_statistics()
        
        if hasattr(self.evidence_finder, 'get_performance_report'):
            # Get detailed performance data from optimized finder
            performance_data = self.evidence_finder.get_performance_report()
            return {
                'integration_stats': base_stats,
                'evidence_finder_performance': performance_data
            }
        else:
            return {
                'integration_stats': base_stats,
                'evidence_finder_performance': None
            }


# Global instance for use in the API
_evidence_integration_service: Optional[EvidenceIntegrationService] = None


def get_evidence_integration_service() -> Optional[EvidenceIntegrationService]:
    """Get the global evidence integration service instance."""
    global _evidence_integration_service
    
    if _evidence_integration_service is None:
        try:
            # Initialize with OpenAI client if available
            openai_client = None
            if os.getenv('OPENAI_API_KEY'):
                openai_client = OpenAI()
            
            _evidence_integration_service = EvidenceIntegrationService(openai_client)
        except Exception as e:
            print(f"[Evidence Integration] Failed to initialize service: {str(e)}")
            _evidence_integration_service = None
    
    return _evidence_integration_service


async def enhance_candidates_with_evidence_urls(
    candidates: List[Dict[str, Any]],
    search_prompt: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Main function to enhance candidates with evidence URLs.
    
    This function can be called from the existing pipeline to add evidence URLs
    to candidate results while maintaining backward compatibility.
    
    Args:
        candidates: List of candidate dictionaries
        search_prompt: Original search prompt for context
        
    Returns:
        Enhanced candidates with evidence URLs (or original if disabled/failed)
    """
    service = get_evidence_integration_service()
    
    if service is None:
        print("[Evidence Integration] Service not available, returning original candidates")
        return candidates
    
    return await service.enhance_candidates_with_evidence(candidates, search_prompt)


def get_evidence_integration_stats() -> Dict[str, Any]:
    """Get evidence integration statistics."""
    service = get_evidence_integration_service()
    
    if service is None:
        return {
            'enabled': False,
            'error': 'Service not initialized'
        }
    
    return {
        'enabled': service.config.enabled,
        'configuration': {
            'use_caching': service.config.use_caching,
            'async_processing': service.config.async_processing,
            'max_candidates': service.config.max_candidates_for_evidence,
            'processing_timeout': service.config.processing_timeout
        },
        'statistics': service.get_statistics()
    }


def get_evidence_performance_report() -> Dict[str, Any]:
    """Get comprehensive evidence performance report."""
    service = get_evidence_integration_service()
    
    if service is None:
        return {
            'enabled': False,
            'error': 'Service not initialized'
        }
    
    return service.get_performance_report()


async def test_evidence_integration():
    """Test function for evidence integration."""
    print("Testing Evidence Integration:")
    print("=" * 50)
    
    # Test candidates
    test_candidates = [
        {
            'id': '1',
            'name': 'John Doe',
            'title': 'VP of Sales',
            'company': 'TechCorp',
            'reasons': [
                'Currently researching Salesforce pricing options for enterprise deployment',
                'Actively comparing CRM solutions including HubSpot and Microsoft Dynamics'
            ],
            'behavioral_data': {
                'behavioral_insight': 'Shows strong interest in CRM technology evaluation',
                'scores': {'cmi': 0.85, 'rbfs': 0.78, 'ias': 0.82}
            }
        },
        {
            'id': '2',
            'name': 'Jane Smith',
            'title': 'Marketing Director',
            'company': 'StartupInc',
            'reasons': [
                'Investigating marketing automation platforms and their integration capabilities'
            ]
        }
    ]
    
    # Test enhancement
    enhanced_candidates = await enhance_candidates_with_evidence_urls(
        test_candidates,
        search_prompt="Find executives evaluating CRM and marketing technology"
    )
    
    print(f"Enhanced {len(enhanced_candidates)} candidates:")
    for candidate in enhanced_candidates:
        print(f"\nCandidate: {candidate['name']}")
        evidence_urls = candidate.get('evidence_urls', [])
        print(f"Evidence URLs: {len(evidence_urls)}")
        print(f"Evidence Summary: {candidate.get('evidence_summary', 'N/A')}")
        print(f"Evidence Confidence: {candidate.get('evidence_confidence', 0.0)}")
    
    # Show statistics
    print(f"\nIntegration Statistics:")
    stats = get_evidence_integration_stats()
    print(f"Enabled: {stats.get('enabled', False)}")
    if 'statistics' in stats:
        for key, value in stats['statistics'].items():
            print(f"{key}: {value}")


if __name__ == '__main__':
    print("Evidence Integration module loaded successfully!")
    print("To test with actual API calls, run: asyncio.run(test_evidence_integration())")
    print("Make sure you have OPENAI_API_KEY environment variable set.")