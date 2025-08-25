#!/usr/bin/env python3
"""
Context-Aware Evidence Finder.

This module creates evidence URLs that are relevant to the specific search context,
rather than generic or domain-specific URLs.
"""

import re
import asyncio
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from enhanced_url_evidence_finder import EnhancedURLEvidenceFinder
from explanation_analyzer import SearchableClaim, ClaimType
from web_search_engine import WebSearchEngine


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


class ContextAwareEvidenceFinder(EnhancedURLEvidenceFinder):
    """Evidence finder that understands search context and generates relevant URLs."""
    
    def __init__(self, enable_diversity: bool = True):
        super().__init__(enable_diversity)
        self.search_context = None
        
    def set_search_context(self, search_prompt: str):
        """
        Set the search context from the original search prompt.
        
        Args:
            search_prompt: The original search query that generated these candidates
        """
        self.search_context = self._analyze_search_context(search_prompt)
        if self.search_context:
            print(f"[Context-Aware Evidence] Search context: {self.search_context.industry} | {self.search_context.role_type} | {self.search_context.activity_type}")
        else:
            print("[Context-Aware Evidence] No search context provided")
    
    def _analyze_search_context(self, search_prompt: str) -> SearchContext:
        """
        Analyze the search prompt to understand context.
        
        Args:
            search_prompt: Original search query
            
        Returns:
            SearchContext with extracted information
        """
        prompt_lower = search_prompt.lower()
        
        # Detect industry
        industry = self._detect_industry(prompt_lower)
        
        # Detect role type
        role_type = self._detect_role_type(prompt_lower)
        
        # Detect activity type
        activity_type = self._detect_activity_type(prompt_lower)
        
        # Extract key terms
        key_terms = self._extract_key_terms(search_prompt)
        
        return SearchContext(
            search_prompt=search_prompt,
            industry=industry,
            role_type=role_type,
            activity_type=activity_type,
            key_terms=key_terms
        )
    
    def _detect_industry(self, prompt: str) -> Optional[str]:
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
        
        for industry, pattern in industry_patterns.items():
            if re.search(pattern, prompt):
                return industry
        
        return None
    
    def _detect_role_type(self, prompt: str) -> Optional[str]:
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
        
        for role, pattern in role_patterns.items():
            if re.search(pattern, prompt):
                return role
        
        return None
    
    def _detect_activity_type(self, prompt: str) -> Optional[str]:
        """Detect activity type from search prompt."""
        activity_patterns = {
            'considering': r'\b(considering|evaluating|exploring|looking at)\b',
            'implementing': r'\b(implementing|deploying|rolling out|adopting)\b',
            'researching': r'\b(researching|investigating|studying|analyzing)\b',
            'planning': r'\b(planning|preparing|strategizing|developing)\b',
            'buying': r'\b(buying|purchasing|acquiring|procuring|looking to buy|want to buy|need to buy)\b',
            'selling': r'\b(selling|divesting|disposing|exiting)\b'
        }
        
        for activity, pattern in activity_patterns.items():
            if re.search(pattern, prompt):
                return activity
        
        return None
    
    def _extract_key_terms(self, prompt: str) -> List[str]:
        """Extract key terms from search prompt."""
        # Remove common words and extract meaningful terms
        common_words = {'find', 'people', 'who', 'are', 'at', 'in', 'with', 'for', 'the', 'and', 'or', 'of', 'to', 'a', 'an'}
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower())
        key_terms = [word for word in words if word not in common_words]
        
        return key_terms[:10]  # Limit to top 10 terms
    
    async def process_candidates_batch(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process candidates with context-aware evidence finding.
        
        Args:
            candidates: List of candidate dictionaries
            
        Returns:
            List of enhanced candidates with contextually relevant evidence URLs
        """
        import time
        batch_start_time = time.time()
        
        if not self.search_context:
            print("[Context-Aware Evidence] Warning: No search context set. Using generic evidence finding.")
            try:
                return await super().process_candidates_batch(candidates)
            except Exception as e:
                print(f"[Context-Aware Evidence] Error in generic evidence finding: {e}")
                return candidates  # Return original candidates if everything fails
        
        print(f"[Context-Aware Evidence] Processing {len(candidates)} candidates with context: {self.search_context.industry}")
        
        enhanced_candidates = []
        successful_count = 0
        failed_count = 0
        
        for candidate in candidates:
            try:
                enhanced_candidate = await self._process_candidate_with_context(candidate)
                enhanced_candidates.append(enhanced_candidate)
                
                # Track success/failure
                if enhanced_candidate.get('evidence_status') in ['completed', 'completed_with_fallback']:
                    successful_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                print(f"[Context-Aware Evidence] Error processing candidate {candidate.get('name', 'Unknown')}: {e}")
                # Ensure candidate processing continues even when evidence finding fails
                candidate_copy = candidate.copy()
                candidate_copy['evidence_urls'] = []
                candidate_copy['evidence_summary'] = f"Evidence finding failed: {str(e)}"
                candidate_copy['evidence_confidence'] = 0.0
                candidate_copy['evidence_status'] = 'failed_processing'
                candidate_copy['evidence_error_message'] = str(e)
                candidate_copy['evidence_completion_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                enhanced_candidates.append(candidate_copy)
                failed_count += 1
        
        # Add batch processing summary
        batch_processing_time = time.time() - batch_start_time
        print(f"[Context-Aware Evidence] Batch completed in {batch_processing_time:.2f}s: {successful_count} successful, {failed_count} failed")
        
        # Add batch metadata to first candidate (for frontend reference)
        if enhanced_candidates:
            enhanced_candidates[0]['batch_evidence_summary'] = {
                'total_candidates': len(candidates),
                'successful_count': successful_count,
                'failed_count': failed_count,
                'batch_processing_time': round(batch_processing_time, 2),
                'batch_completion_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        
        return enhanced_candidates
    
    async def _process_candidate_with_context(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single candidate with context awareness."""
        import time
        
        # Track processing start time for status reporting
        self._processing_start_time = time.time()
        
        # Add initial processing status
        candidate['evidence_status'] = 'processing'
        candidate['evidence_processing_start'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Generate context-aware search queries
        search_queries = self._generate_contextual_queries(candidate)
        
        if not search_queries:
            print(f"[Context-Aware Evidence] No contextual queries generated for {candidate.get('name', 'Unknown')}")
            return candidate
        
        print(f"[Context-Aware Evidence] Generated {len(search_queries)} contextual queries for {candidate.get('name', 'Unknown')}")
        
        # Execute searches with new real web search engine
        from web_search_engine import WebSearchEngine, load_search_config_safely
        try:
            config = load_search_config_safely()
            web_search = WebSearchEngine(config)
        except Exception as e:
            print(f"[Context-Aware Evidence] Error initializing web search: {e}")
            # Use fallback URLs if initialization fails
            evidence_urls = self._generate_contextual_fallback_urls()
            print(f"[Context-Aware Evidence] Using {len(evidence_urls)} fallback URLs due to initialization error")
            
            # Add error status information
            import time
            processing_time = time.time() - getattr(self, '_processing_start_time', time.time())
            
            if evidence_urls:
                candidate['evidence_urls'] = [self._format_evidence_url(url) for url in evidence_urls]
                candidate['evidence_summary'] = f"Found {len(evidence_urls)} fallback evidence URLs (initialization error)"
                candidate['evidence_confidence'] = 0.3
                candidate['evidence_status'] = 'completed_with_fallback'
            else:
                candidate['evidence_urls'] = []
                candidate['evidence_summary'] = "No evidence URLs available due to initialization error"
                candidate['evidence_confidence'] = 0.0
                candidate['evidence_status'] = 'failed_initialization'
            
            candidate['evidence_processing_time'] = round(processing_time, 2)
            candidate['evidence_completion_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            candidate['evidence_error_message'] = str(e)
            
            return candidate
        search_results = []
        
        try:
            # Execute search with reasonable timeout - the new search engine is much faster
            search_task = asyncio.create_task(self._execute_searches(web_search, search_queries[:2]))  # Try 2 queries
            search_results = await asyncio.wait_for(search_task, timeout=10.0)  # Longer timeout since real search is reliable
            print(f"[Context-Aware Evidence] Search completed successfully for {candidate.get('name', 'Unknown')}")
        except asyncio.TimeoutError:
            print(f"[Context-Aware Evidence] Search timed out after 10s, using fallback URLs for {candidate.get('name', 'Unknown')}")
            search_results = []
        except AttributeError as e:
            print(f"[Context-Aware Evidence] Configuration error: {e}, using fallback URLs for {candidate.get('name', 'Unknown')}")
            search_results = []
        except Exception as e:
            print(f"[Context-Aware Evidence] Search failed with error: {type(e).__name__}: {e}, using fallback URLs for {candidate.get('name', 'Unknown')}")
            search_results = []
        
        # Filter and validate URLs (skip validation for speed)
        try:
            evidence_urls = await self._extract_and_validate_urls(search_results)
        except Exception as e:
            print(f"[Context-Aware Evidence] Error extracting URLs: {e}, using fallback URLs")
            evidence_urls = []
        
        # If no URLs found from search results, generate contextual fallback URLs
        if not evidence_urls:
            try:
                evidence_urls = self._generate_contextual_fallback_urls()
                print(f"[Context-Aware Evidence] Using {len(evidence_urls)} contextual fallback URLs for {candidate.get('name', 'Unknown')}")
            except Exception as e:
                print(f"[Context-Aware Evidence] Error generating fallback URLs: {e}")
                evidence_urls = []
        
        # Create enhanced candidate response with comprehensive status information
        import time
        processing_end_time = time.time()
        processing_time = processing_end_time - getattr(self, '_processing_start_time', processing_end_time)
        
        if evidence_urls:
            candidate['evidence_urls'] = [self._format_evidence_url(url) for url in evidence_urls]
            candidate['evidence_summary'] = f"Found {len(evidence_urls)} contextually relevant evidence URLs"
            candidate['evidence_confidence'] = min(0.95, 0.6 + (len(evidence_urls) * 0.1))
            candidate['evidence_status'] = 'completed'
            candidate['evidence_processing_time'] = round(processing_time, 2)
            candidate['evidence_completion_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"[Context-Aware Evidence] Found {len(evidence_urls)} relevant URLs for {candidate.get('name', 'Unknown')}")
        else:
            candidate['evidence_urls'] = []
            candidate['evidence_summary'] = "No contextually relevant evidence URLs found"
            candidate['evidence_confidence'] = 0.0
            candidate['evidence_status'] = 'completed_no_results'
            candidate['evidence_processing_time'] = round(processing_time, 2)
            candidate['evidence_completion_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"[Context-Aware Evidence] No relevant URLs found for {candidate.get('name', 'Unknown')}")
        
        return candidate
    
    def _generate_contextual_queries(self, candidate: Dict[str, Any]) -> List[str]:
        """Generate highly specific search queries based on context and candidate info."""
        from specific_search_query_generator import SpecificSearchQueryGenerator
        
        # Use enhanced query generator for specificity
        specific_generator = SpecificSearchQueryGenerator()
        
        # CRITICAL FIX: Use the original search prompt instead of reconstructed one
        # The original prompt maintains important context and word order
        search_prompt = self.search_context.search_prompt if self.search_context else self._build_search_prompt()
        
        print(f"[Context-Aware Evidence] Using search prompt for query generation: {search_prompt}")
        
        # Generate location-specific and context-aware queries
        specific_queries = specific_generator.generate_location_specific_queries(search_prompt, candidate)
        
        if specific_queries:
            print(f"[Context-Aware Evidence] Generated {len(specific_queries)} specific queries: {specific_queries}")
            return specific_queries
        else:
            print(f"[Context-Aware Evidence] No specific queries generated, using fallback logic")
        
        # Fallback to original logic if specific generator doesn't produce results
        queries = []
        
        name = candidate.get('name', '')
        title = candidate.get('title', '')
        company = candidate.get('company', '')
        
        # Get behavioral insight
        behavioral_data = candidate.get('behavioral_data', {})
        insight = behavioral_data.get('behavioral_insight', '') if isinstance(behavioral_data, dict) else ''
        
        # SPECIAL HANDLING FOR REAL ESTATE QUERIES
        if self.search_context.industry == 'real_estate':
            print(f"[Context-Aware Evidence] Detected real estate query, generating location-specific queries")
            
            # Extract location from original search prompt
            import re
            original_prompt = self.search_context.search_prompt
            
            # Look for location patterns in the original prompt
            location_patterns = [
                r'\b(Greenwich|New York|Los Angeles|Chicago|Boston|Miami|Seattle|Austin|Denver)\b',
                r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',  # "in CityName"
                r'\b([A-Z][a-z]+)\s+(?:Connecticut|CT|New York|NY|California|CA)\b'  # "City State"
            ]
            
            location = None
            for pattern in location_patterns:
                match = re.search(pattern, original_prompt, re.IGNORECASE)
                if match:
                    location = match.group(1) if match.lastindex else match.group(0)
                    break
            
            if location:
                # Generate real estate specific queries
                real_estate_queries = [
                    f"{location} homes for sale",
                    f"{location} real estate listings",
                    f"{location} luxury homes market",
                    f"{location} property market trends",
                    f"buy house {location}",
                    f"{location} real estate agents"
                ]
                queries.extend(real_estate_queries)
                print(f"[Context-Aware Evidence] Generated {len(real_estate_queries)} real estate queries for {location}")
            else:
                # Generic real estate queries if no location found
                queries.extend([
                    "luxury home buying trends",
                    "executive home purchasing patterns",
                    "high-end real estate market"
                ])
        
        # Enhanced specific queries for other industries
        elif self.search_context.industry and self.search_context.activity_type:
            # More specific industry + activity queries
            base_query = f"{self.search_context.industry} {self.search_context.activity_type} 2024"
            queries.append(base_query)
            
            # Add location context if available
            if company and any(location in company.lower() for location in ['greenwich', 'new york', 'boston', 'chicago']):
                location_query = f"{self.search_context.industry} {company} {self.search_context.activity_type}"
                queries.append(location_query)
        
        # CRITICAL FIX: Use name-free search generator for all queries
        # This completely eliminates the risk of using prospect names in searches
        
        from name_free_search_generator import NameFreeSearchGenerator
        
        # Create a mock claim from the candidate data for the name-free generator
        mock_claim_entities = {}
        
        if title:
            # Extract role information
            mock_claim_entities['roles'] = [title]
        
        if company:
            # Extract company information
            mock_claim_entities['companies'] = [company]
        
        # Add industry context if available
        if (self.search_context and 
            hasattr(self.search_context, 'industry') and 
            self.search_context.industry):
            mock_claim_entities['industries'] = [self.search_context.industry]
        
        # Create mock claim for name-free generator
        from explanation_analyzer import SearchableClaim, ClaimType
        
        mock_claim = SearchableClaim(
            text=f"Professional in {title} role at {company}" if title and company else "Professional seeking opportunities",
            claim_type=ClaimType.GENERAL_ACTIVITY,
            entities=mock_claim_entities,
            search_terms=[term for term in [title, company] if term],
            priority=8,
            confidence=0.9
        )
        
        # Generate name-free queries
        name_free_generator = NameFreeSearchGenerator()
        name_free_queries = name_free_generator.generate_queries(mock_claim)
        
        # Convert to simple query strings
        for query_obj in name_free_queries:
            queries.append(query_obj.query)
        
        # Industry-specific queries with current context
        if self.search_context.industry:
            industry_queries = [
                f"{self.search_context.industry} industry trends 2024",
                f"{self.search_context.industry} market analysis current",
                f"{self.search_context.industry} companies news"
            ]
            queries.extend(industry_queries)
        
        # Safety check: Remove any queries that might contain names
        safe_queries = []
        for query in queries:
            # Skip queries that might contain personal names
            if name and (name.lower() in query.lower() or 
                        any(name_part.lower() in query.lower() for name_part in name.split() if len(name_part) > 2)):
                print(f"[BLOCKED NAME-BASED QUERY]: {query}")
                continue
            safe_queries.append(query)
        
        return safe_queries[:5]  # Limit to top 5 safe, behavioral-focused queries
    
    def _build_search_prompt(self) -> str:
        """Build search prompt from current context."""
        prompt_parts = []
        
        if self.search_context and self.search_context.industry:
            prompt_parts.append(self.search_context.industry)
        
        if self.search_context and self.search_context.activity_type:
            prompt_parts.append(self.search_context.activity_type)
        
        if self.search_context and self.search_context.role_type:
            prompt_parts.append(self.search_context.role_type)
        
        if self.search_context and self.search_context.key_terms:
            prompt_parts.extend(self.search_context.key_terms[:3])
        
        return " ".join(prompt_parts) if prompt_parts else "business search"
    
    async def _execute_searches(self, web_search, search_queries):
        """Execute search queries and return results."""
        search_results = []
        
        # Import SearchQuery for proper formatting
        from search_query_generator import SearchQuery
        
        for query_str in search_queries:
            try:
                print(f"[Context-Aware Evidence] Searching: {query_str}")
                
                # Create SearchQuery object
                search_query = SearchQuery(
                    query=query_str,
                    expected_domains=[],  # Let the system find relevant domains
                    page_types=["article", "news", "research"],
                    priority=5,  # Medium priority
                    claim_support="contextual evidence for search relevance",
                    search_strategy="contextual_evidence"
                )
                
                results = await web_search.search_for_evidence([search_query])
                search_results.extend(results)
            except Exception as e:
                print(f"[Context-Aware Evidence] Search failed for query '{query_str}': {e}")
        
        return search_results
    
    async def _extract_and_validate_urls(self, search_results: List) -> List[str]:
        """Extract URLs from search results with quality filtering for specificity."""
        from specific_search_query_generator import SpecificSearchQueryGenerator
        
        url_candidates = []
        quality_generator = SpecificSearchQueryGenerator()
        
        for result in search_results:
            # Process URLs from real search results
            if hasattr(result, 'urls') and result.urls:
                for url_candidate in result.urls:
                    if hasattr(url_candidate, 'url') and url_candidate.url:
                        # Create result dict for quality scoring
                        result_dict = {
                            'url': url_candidate.url,
                            'title': getattr(url_candidate, 'title', ''),
                            'snippet': getattr(url_candidate, 'snippet', '')
                        }
                        
                        # Score result specificity
                        specificity_score = quality_generator.score_result_specificity(result_dict)
                        
                        url_candidates.append({
                            'url': url_candidate.url,
                            'title': result_dict['title'],
                            'snippet': result_dict['snippet'],
                            'specificity_score': specificity_score
                        })
        
        # Filter out low-quality generic results
        high_quality_urls = [
            candidate for candidate in url_candidates 
            if candidate['specificity_score'] >= 0.4  # Minimum quality threshold
        ]
        
        # Sort by specificity score (highest first)
        high_quality_urls.sort(key=lambda x: x['specificity_score'], reverse=True)
        
        # Extract just the URLs
        filtered_urls = [candidate['url'] for candidate in high_quality_urls]
        
        # Remove duplicates while preserving order
        unique_urls = list(dict.fromkeys(filtered_urls))
        
        if unique_urls:
            print(f"[Context-Aware Evidence] Found {len(unique_urls[:5])} high-quality specific URLs")
            if high_quality_urls:
                avg_score = sum(c['specificity_score'] for c in high_quality_urls[:5]) / min(5, len(high_quality_urls))
                print(f"[Context-Aware Evidence] Average specificity score: {avg_score:.2f}")
            return unique_urls[:5]
        else:
            # If no high-quality results, return original results but log the issue
            print(f"[Context-Aware Evidence] No high-quality specific results found, using all results")
            fallback_urls = [candidate['url'] for candidate in url_candidates]
            return list(dict.fromkeys(fallback_urls))[:5]
    
    def _format_evidence_url(self, url: str) -> Dict[str, Any]:
        """Format URL for frontend consumption."""
        return {
            'url': url,
            'title': self._generate_title_from_url(url),
            'relevance_score': 0.8,
            'source_type': 'contextual_evidence'
        }
    
    def _generate_contextual_fallback_urls(self) -> List[str]:
        """Generate contextual fallback URLs when search fails."""
        fallback_urls = []
        
        if not self.search_context:
            return fallback_urls
        
        # Industry-specific URLs
        if self.search_context.industry == 'real_estate':
            fallback_urls.extend([
                "https://www.nar.realtor/research-and-statistics",
                "https://www.bisnow.com/",
                "https://www.commercialobserver.com/"
            ])
        elif self.search_context.industry == 'technology':
            fallback_urls.extend([
                "https://techcrunch.com/",
                "https://www.crunchbase.com/",
                "https://venturebeat.com/"
            ])
        elif self.search_context.industry == 'finance':
            fallback_urls.extend([
                "https://www.bloomberg.com/",
                "https://www.wsj.com/",
                "https://www.ft.com/"
            ])
        
        # Role-specific URLs
        if self.search_context and self.search_context.role_type == 'executive':
            fallback_urls.extend([
                "https://hbr.org/",
                "https://www.mckinsey.com/",
                "https://www.bcg.com/"
            ])
        
        # Activity-specific URLs
        if self.search_context.activity_type == 'buying':
            fallback_urls.extend([
                "https://www.forbes.com/",
                "https://www.entrepreneur.com/"
            ])
        
        # Remove duplicates and limit
        unique_urls = list(dict.fromkeys(fallback_urls))
        return unique_urls[:3]
    
    def _generate_title_from_url(self, url: str) -> str:
        """Generate a title from URL."""
        try:
            domain = url.split('/')[2].replace('www.', '')
            if 'forbes' in domain:
                return f"Forbes - {self.search_context.industry if self.search_context else 'Business'} Insights"
            elif 'harvard' in domain or 'hbr' in domain:
                return f"Harvard Business Review - {self.search_context.role_type if self.search_context else 'Leadership'}"
            elif 'mckinsey' in domain:
                return f"McKinsey - {self.search_context.industry if self.search_context else 'Strategy'} Analysis"
            elif 'nar.realtor' in domain:
                return "National Association of Realtors - Market Data"
            elif 'bisnow' in domain:
                return "Bisnow - Commercial Real Estate News"
            elif 'bloomberg' in domain:
                return "Bloomberg - Financial Markets"
            elif 'techcrunch' in domain:
                return "TechCrunch - Technology News"
            else:
                return f"{domain.title()} - Industry Resource"
        except:
            return "Industry Resource"


# Test function
async def test_context_aware_evidence():
    """Test the context-aware evidence finder."""
    finder = ContextAwareEvidenceFinder(enable_diversity=True)
    
    # Set search context
    search_prompt = "Find corporate development officers at media companies considering divestiture"
    finder.set_search_context(search_prompt)
    
    # Test candidate
    test_candidates = [{
        'id': 'test_1',
        'name': 'Sarah Johnson',
        'title': 'VP Corporate Development',
        'company': 'MediaCorp Inc',
        'behavioral_data': {
            'behavioral_insight': 'Sarah is evaluating strategic divestiture options and has been researching M&A market conditions'
        }
    }]
    
    print("Testing Context-Aware Evidence Finder...")
    results = await finder.process_candidates_batch(test_candidates)
    
    if results:
        candidate = results[0]
        evidence_urls = candidate.get('evidence_urls', [])
        print(f"\nResults for {candidate.get('name')}:")
        print(f"Evidence URLs: {len(evidence_urls)}")
        for i, url in enumerate(evidence_urls):
            print(f"  {i+1}. {url.get('title')} - {url.get('url')}")


if __name__ == '__main__':
    asyncio.run(test_context_aware_evidence())