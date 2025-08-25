#!/usr/bin/env python3
"""
URL Validator for Evidence URLs.

This module validates that evidence URLs are accessible and return valid responses
before including them in candidate results.
"""

import asyncio
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class URLValidationResult:
    """Result of URL validation check."""
    url: str
    is_valid: bool
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    response_time: Optional[float] = None


class URLValidator:
    """Validates evidence URLs to ensure they're accessible."""
    
    def __init__(self, timeout: float = 5.0, max_concurrent: int = 10):
        """
        Initialize URL validator.
        
        Args:
            timeout: Request timeout in seconds
            max_concurrent: Maximum concurrent requests
        """
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        
        # User agent to avoid bot blocking
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.executor.shutdown(wait=True)
    
    def _validate_url_sync(self, url: str) -> URLValidationResult:
        """
        Validate a single URL synchronously.
        
        Args:
            url: URL to validate
            
        Returns:
            URLValidationResult with validation status
        """
        start_time = time.time()
        
        try:
            # Create request with custom headers
            request = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
            
            # Use HEAD request to check if URL exists without downloading content
            request.get_method = lambda: 'HEAD'
            
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_time = time.time() - start_time
                status_code = response.getcode()
                
                # Consider 2xx and 3xx status codes as valid
                is_valid = 200 <= status_code < 400
                
                return URLValidationResult(
                    url=url,
                    is_valid=is_valid,
                    status_code=status_code,
                    response_time=response_time
                )
                
        except urllib.error.HTTPError as e:
            return URLValidationResult(
                url=url,
                is_valid=False,
                status_code=e.code,
                error_message=f"HTTP {e.code}: {e.reason}",
                response_time=time.time() - start_time
            )
        except urllib.error.URLError as e:
            return URLValidationResult(
                url=url,
                is_valid=False,
                error_message=f"URL error: {str(e.reason)}",
                response_time=time.time() - start_time
            )
        except Exception as e:
            return URLValidationResult(
                url=url,
                is_valid=False,
                error_message=f"Unexpected error: {str(e)}",
                response_time=time.time() - start_time
            )
    
    async def validate_url(self, url: str) -> URLValidationResult:
        """
        Validate a single URL asynchronously.
        
        Args:
            url: URL to validate
            
        Returns:
            URLValidationResult with validation status
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._validate_url_sync, url)
    
    async def validate_urls(self, urls: List[str]) -> List[URLValidationResult]:
        """
        Validate multiple URLs concurrently.
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            List of URLValidationResult objects
        """
        if not urls:
            return []
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def validate_with_semaphore(url: str) -> URLValidationResult:
            async with semaphore:
                return await self.validate_url(url)
        
        # Run validations concurrently
        tasks = [validate_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions that occurred
        validated_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                validated_results.append(URLValidationResult(
                    url=urls[i],
                    is_valid=False,
                    error_message=f"Validation failed: {str(result)}"
                ))
            else:
                validated_results.append(result)
        
        return validated_results
    
    def filter_valid_urls(self, urls: List[str], validation_results: List[URLValidationResult]) -> List[str]:
        """
        Filter URLs to only include valid ones.
        
        Args:
            urls: Original list of URLs
            validation_results: Validation results for the URLs
            
        Returns:
            List of valid URLs
        """
        valid_urls = []
        for result in validation_results:
            if result.is_valid:
                valid_urls.append(result.url)
        
        return valid_urls


async def validate_evidence_urls(evidence_urls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate evidence URLs and filter out invalid ones.
    
    Args:
        evidence_urls: List of evidence URL dictionaries
        
    Returns:
        List of evidence URLs with only valid URLs
    """
    if not evidence_urls:
        return []
    
    # Extract URLs for validation
    urls_to_validate = [item.get('url') for item in evidence_urls if item.get('url')]
    
    if not urls_to_validate:
        return evidence_urls
    
    print(f"[URL Validator] Validating {len(urls_to_validate)} evidence URLs...")
    
    async with URLValidator(timeout=3.0, max_concurrent=5) as validator:
        validation_results = await validator.validate_urls(urls_to_validate)
    
    # Filter evidence URLs based on validation results
    valid_evidence = []
    invalid_count = 0
    
    for evidence_item in evidence_urls:
        url = evidence_item.get('url')
        if not url:
            continue
        
        # Find validation result for this URL
        validation_result = next((r for r in validation_results if r.url == url), None)
        
        if validation_result and validation_result.is_valid:
            valid_evidence.append(evidence_item)
        else:
            invalid_count += 1
            error_msg = validation_result.error_message if validation_result else "No validation result"
            print(f"[URL Validator] Filtered out invalid URL: {url} ({error_msg})")
    
    print(f"[URL Validator] Kept {len(valid_evidence)}/{len(evidence_urls)} URLs ({invalid_count} filtered out)")
    
    return valid_evidence


# Quick test function
async def test_url_validator():
    """Test the URL validator with sample URLs."""
    test_urls = [
        "https://www.google.com",  # Should be valid
        "https://www.example.com",  # Should be valid
        "https://nonexistent-domain-12345.com",  # Should be invalid
        "https://httpstat.us/404",  # Should be invalid (404)
        "https://httpstat.us/200",  # Should be valid
    ]
    
    print("Testing URL Validator...")
    
    async with URLValidator() as validator:
        results = await validator.validate_urls(test_urls)
    
    for result in results:
        status = "✅ VALID" if result.is_valid else "❌ INVALID"
        details = f"({result.status_code})" if result.status_code else f"({result.error_message})"
        print(f"{status} {result.url} {details}")


if __name__ == '__main__':
    asyncio.run(test_url_validator())