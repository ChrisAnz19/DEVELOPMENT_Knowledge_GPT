#!/usr/bin/env python3
"""
Evidence Cache and Performance Optimization for URL Evidence Finder.

This module provides caching, performance monitoring, and optimization
features to improve the efficiency of evidence gathering operations.
"""

import time
import hashlib
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import OrderedDict
from threading import Lock

from evidence_models import EvidenceURL, SearchableClaim
from search_query_generator import SearchQuery
from web_search_engine import SearchResult


@dataclass
class CacheEntry:
    """Represents a cached search result."""
    key: str
    data: Any
    timestamp: float
    access_count: int
    last_accessed: float
    ttl: float  # Time to live in seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.timestamp > self.ttl
    
    def is_stale(self, max_age: float = 3600) -> bool:
        """Check if cache entry is stale (older than max_age)."""
        return time.time() - self.timestamp > max_age


class EvidenceCache:
    """LRU cache with TTL for evidence search results."""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl  # 1 hour default TTL
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = Lock()
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired_entries': 0,
            'total_requests': 0
        }
    
    def _generate_cache_key(self, data: Any) -> str:
        """Generate a consistent cache key from data."""
        if isinstance(data, str):
            content = data
        elif isinstance(data, dict):
            content = json.dumps(data, sort_keys=True)
        elif hasattr(data, '__dict__'):
            content = json.dumps(asdict(data) if hasattr(data, '__dataclass_fields__') else data.__dict__, sort_keys=True)
        else:
            content = str(data)
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with self.lock:
            self.stats['total_requests'] += 1
            
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self.cache[key]
                self.stats['expired_entries'] += 1
                self.stats['misses'] += 1
                return None
            
            # Update access info and move to end (most recently used)
            entry.access_count += 1
            entry.last_accessed = time.time()
            self.cache.move_to_end(key)
            
            self.stats['hits'] += 1
            return entry.data
    
    def put(self, key: str, data: Any, ttl: Optional[float] = None) -> None:
        """Put item in cache."""
        with self.lock:
            current_time = time.time()
            ttl = ttl or self.default_ttl
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                data=data,
                timestamp=current_time,
                access_count=1,
                last_accessed=current_time,
                ttl=ttl
            )
            
            # Add to cache
            self.cache[key] = entry
            self.cache.move_to_end(key)
            
            # Evict if over capacity
            while len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.stats['evictions'] += 1
    
    def get_or_compute(self, key: str, compute_func, ttl: Optional[float] = None) -> Any:
        """Get from cache or compute and cache the result."""
        cached_result = self.get(key)
        if cached_result is not None:
            return cached_result
        
        # Compute result
        result = compute_func()
        self.put(key, result, ttl)
        return result
    
    def invalidate(self, pattern: Optional[str] = None) -> int:
        """Invalidate cache entries matching pattern."""
        with self.lock:
            if pattern is None:
                # Clear all
                count = len(self.cache)
                self.cache.clear()
                return count
            
            # Remove entries matching pattern
            keys_to_remove = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self.cache[key]
            
            return len(keys_to_remove)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries from cache."""
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            self.stats['expired_entries'] += len(expired_keys)
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            hit_rate = (
                self.stats['hits'] / self.stats['total_requests']
                if self.stats['total_requests'] > 0 else 0.0
            )
            
            return {
                **self.stats,
                'hit_rate': hit_rate,
                'cache_size': len(self.cache),
                'max_size': self.max_size
            }


class SearchResultCache:
    """Specialized cache for search results."""
    
    def __init__(self, cache: EvidenceCache):
        self.cache = cache
    
    def get_search_results(self, query: SearchQuery) -> Optional[SearchResult]:
        """Get cached search results for a query."""
        cache_key = f"search:{self.cache._generate_cache_key(query.query)}"
        return self.cache.get(cache_key)
    
    def cache_search_results(self, query: SearchQuery, result: SearchResult, ttl: float = 1800) -> None:
        """Cache search results for a query (30 min default TTL)."""
        cache_key = f"search:{self.cache._generate_cache_key(query.query)}"
        self.cache.put(cache_key, result, ttl)
    
    def get_evidence_urls(self, claim: SearchableClaim) -> Optional[List[EvidenceURL]]:
        """Get cached evidence URLs for a claim."""
        cache_key = f"evidence:{self.cache._generate_cache_key(claim.text)}"
        return self.cache.get(cache_key)
    
    def cache_evidence_urls(self, claim: SearchableClaim, evidence_urls: List[EvidenceURL], ttl: float = 3600) -> None:
        """Cache evidence URLs for a claim (1 hour default TTL)."""
        cache_key = f"evidence:{self.cache._generate_cache_key(claim.text)}"
        self.cache.put(cache_key, evidence_urls, ttl)


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.metrics = {
            'operation_times': {},
            'operation_counts': {},
            'error_counts': {},
            'cache_performance': {},
            'api_usage': {
                'requests_made': 0,
                'tokens_used': 0,
                'rate_limit_hits': 0
            }
        }
        self.lock = Lock()
    
    def record_operation_time(self, operation: str, duration: float) -> None:
        """Record the duration of an operation."""
        with self.lock:
            if operation not in self.metrics['operation_times']:
                self.metrics['operation_times'][operation] = []
            
            self.metrics['operation_times'][operation].append(duration)
            
            # Keep only last 100 measurements
            if len(self.metrics['operation_times'][operation]) > 100:
                self.metrics['operation_times'][operation] = self.metrics['operation_times'][operation][-100:]
            
            # Update count
            self.metrics['operation_counts'][operation] = self.metrics['operation_counts'].get(operation, 0) + 1
    
    def record_error(self, operation: str, error_type: str) -> None:
        """Record an error occurrence."""
        with self.lock:
            key = f"{operation}:{error_type}"
            self.metrics['error_counts'][key] = self.metrics['error_counts'].get(key, 0) + 1
    
    def record_api_usage(self, requests: int = 1, tokens: int = 0) -> None:
        """Record API usage."""
        with self.lock:
            self.metrics['api_usage']['requests_made'] += requests
            self.metrics['api_usage']['tokens_used'] += tokens
    
    def record_rate_limit_hit(self) -> None:
        """Record a rate limit hit."""
        with self.lock:
            self.metrics['api_usage']['rate_limit_hits'] += 1
    
    def get_operation_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for a specific operation."""
        with self.lock:
            times = self.metrics['operation_times'].get(operation, [])
            if not times:
                return {'count': 0, 'avg_time': 0.0, 'min_time': 0.0, 'max_time': 0.0}
            
            return {
                'count': len(times),
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'total_time': sum(times)
            }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get all performance statistics."""
        with self.lock:
            stats = {
                'operations': {},
                'errors': dict(self.metrics['error_counts']),
                'api_usage': dict(self.metrics['api_usage'])
            }
            
            for operation in self.metrics['operation_times']:
                stats['operations'][operation] = self.get_operation_stats(operation)
            
            return stats


class BatchProcessor:
    """Optimize batch processing of evidence gathering."""
    
    def __init__(self, cache: EvidenceCache, monitor: PerformanceMonitor):
        self.cache = cache
        self.monitor = monitor
        self.search_cache = SearchResultCache(cache)
    
    async def process_claims_batch(
        self,
        claims: List[SearchableClaim],
        search_function,
        max_concurrent: int = 5
    ) -> Dict[str, List[EvidenceURL]]:
        """Process multiple claims with caching and concurrency control."""
        start_time = time.time()
        
        # Separate cached and uncached claims
        cached_results = {}
        uncached_claims = []
        
        for claim in claims:
            cached_evidence = self.search_cache.get_evidence_urls(claim)
            if cached_evidence is not None:
                claim_key = self.cache._generate_cache_key(claim.text)
                cached_results[claim_key] = cached_evidence
            else:
                uncached_claims.append(claim)
        
        print(f"[Batch Processor] Found {len(cached_results)} cached results, processing {len(uncached_claims)} new claims")
        
        # Process uncached claims with concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single_claim(claim: SearchableClaim) -> Tuple[str, List[EvidenceURL]]:
            async with semaphore:
                try:
                    evidence_urls = await search_function(claim)
                    
                    # Cache the results
                    self.search_cache.cache_evidence_urls(claim, evidence_urls)
                    
                    claim_key = self.cache._generate_cache_key(claim.text)
                    return claim_key, evidence_urls
                
                except Exception as e:
                    self.monitor.record_error('batch_process_claim', type(e).__name__)
                    claim_key = self.cache._generate_cache_key(claim.text)
                    return claim_key, []
        
        # Execute uncached claims concurrently
        if uncached_claims:
            tasks = [process_single_claim(claim) for claim in uncached_claims]
            uncached_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in uncached_results:
                if isinstance(result, Exception):
                    self.monitor.record_error('batch_process', type(result).__name__)
                else:
                    claim_key, evidence_urls = result
                    cached_results[claim_key] = evidence_urls
        
        processing_time = time.time() - start_time
        self.monitor.record_operation_time('batch_process_claims', processing_time)
        
        return cached_results
    
    def deduplicate_queries(self, queries: List[SearchQuery]) -> List[SearchQuery]:
        """Remove duplicate queries to optimize search operations."""
        seen_queries = set()
        unique_queries = []
        
        for query in queries:
            query_key = self.cache._generate_cache_key(query.query)
            if query_key not in seen_queries:
                seen_queries.add(query_key)
                unique_queries.append(query)
        
        dedup_count = len(queries) - len(unique_queries)
        if dedup_count > 0:
            print(f"[Batch Processor] Deduplicated {dedup_count} queries")
        
        return unique_queries


class OptimizedEvidenceFinder:
    """Evidence finder with performance optimizations and caching."""
    
    def __init__(self, base_finder, cache_size: int = 1000):
        self.base_finder = base_finder
        self.cache = EvidenceCache(max_size=cache_size)
        self.monitor = PerformanceMonitor()
        self.batch_processor = BatchProcessor(self.cache, self.monitor)
        
        # Override base finder's web search engine to add caching
        self._wrap_search_engine()
    
    def _wrap_search_engine(self):
        """Wrap the web search engine to add caching."""
        original_search = self.base_finder.web_search_engine.search_for_evidence
        search_cache = SearchResultCache(self.cache)
        
        async def cached_search(queries: List[SearchQuery]) -> List[SearchResult]:
            cached_results = []
            uncached_queries = []
            
            # Check cache for each query
            for query in queries:
                cached_result = search_cache.get_search_results(query)
                if cached_result is not None:
                    cached_results.append(cached_result)
                else:
                    uncached_queries.append(query)
            
            # Execute uncached queries
            if uncached_queries:
                start_time = time.time()
                new_results = await original_search(uncached_queries)
                search_time = time.time() - start_time
                
                self.monitor.record_operation_time('web_search', search_time)
                self.monitor.record_api_usage(requests=len(uncached_queries))
                
                # Cache new results
                for query, result in zip(uncached_queries, new_results):
                    if result.success:
                        search_cache.cache_search_results(query, result)
                
                cached_results.extend(new_results)
            
            return cached_results
        
        # Replace the search method
        self.base_finder.web_search_engine.search_for_evidence = cached_search
    
    async def find_evidence_optimized(
        self,
        explanations: List[str],
        candidate_context: Optional[Dict[str, Any]] = None
    ) -> List[EvidenceURL]:
        """Find evidence with caching and performance monitoring."""
        start_time = time.time()
        
        try:
            result = await self.base_finder.find_evidence(explanations, candidate_context)
            
            processing_time = time.time() - start_time
            self.monitor.record_operation_time('find_evidence', processing_time)
            
            return result
        
        except Exception as e:
            self.monitor.record_error('find_evidence', type(e).__name__)
            raise
    
    async def process_candidates_optimized(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process candidates with full optimization."""
        start_time = time.time()
        
        try:
            # Use the base finder's optimized batch processing
            result = await self.base_finder.process_candidates_batch(candidates)
            
            processing_time = time.time() - start_time
            self.monitor.record_operation_time('process_candidates_batch', processing_time)
            
            return result
        
        except Exception as e:
            self.monitor.record_error('process_candidates_batch', type(e).__name__)
            raise
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        return {
            'cache_stats': self.cache.get_stats(),
            'performance_stats': self.monitor.get_all_stats(),
            'optimization_summary': {
                'cache_enabled': True,
                'batch_processing': True,
                'concurrent_searches': True,
                'query_deduplication': True
            }
        }
    
    def cleanup_cache(self) -> Dict[str, int]:
        """Clean up expired cache entries."""
        expired_count = self.cache.cleanup_expired()
        return {
            'expired_entries_removed': expired_count,
            'current_cache_size': len(self.cache.cache)
        }


def test_evidence_cache():
    """Test function for evidence cache."""
    print("Testing Evidence Cache:")
    print("=" * 50)
    
    # Test basic cache operations
    cache = EvidenceCache(max_size=5, default_ttl=2)
    
    # Test put and get
    cache.put("key1", "value1")
    cache.put("key2", "value2")
    
    print(f"Get key1: {cache.get('key1')}")
    print(f"Get key2: {cache.get('key2')}")
    print(f"Get nonexistent: {cache.get('key3')}")
    
    # Test TTL expiration
    print("\nTesting TTL expiration (waiting 3 seconds)...")
    time.sleep(3)
    print(f"Get key1 after TTL: {cache.get('key1')}")
    
    # Test cache stats
    print(f"\nCache stats: {cache.get_stats()}")
    
    # Test performance monitor
    print("\nTesting Performance Monitor:")
    monitor = PerformanceMonitor()
    
    monitor.record_operation_time("test_op", 1.5)
    monitor.record_operation_time("test_op", 2.0)
    monitor.record_error("test_op", "ValueError")
    
    print(f"Operation stats: {monitor.get_operation_stats('test_op')}")
    print(f"All stats: {monitor.get_all_stats()}")


if __name__ == '__main__':
    test_evidence_cache()