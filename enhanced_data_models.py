#!/usr/bin/env python3
"""
Enhanced Data Models and Configuration for URL Diversity Enhancement.

This module provides simplified data models and configuration classes
for the diversity enhancement system.
"""

from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class SourceTier(Enum):
    """Classification of source tiers by market presence."""
    MAJOR = "major"
    MID_TIER = "mid-tier"
    NICHE = "niche"
    ALTERNATIVE = "alternative"
    EMERGING = "emerging"


class EvidenceType(Enum):
    """Types of evidence that URLs can provide."""
    OFFICIAL_COMPANY_PAGE = "official_company_page"
    PRODUCT_PAGE = "product_page"
    PRICING_PAGE = "pricing_page"
    DOCUMENTATION = "documentation"
    NEWS_ARTICLE = "news_article"
    CASE_STUDY = "case_study"
    COMPARISON_SITE = "comparison_site"
    INDUSTRY_REPORT = "industry_report"
    REVIEW_SITE = "review_site"
    BLOG_POST = "blog_post"
    GENERAL_INFORMATION = "general_information"


@dataclass
class EnhancedEvidenceURL:
    """Enhanced Evidence URL with diversity-specific fields."""
    url: str
    title: str
    description: str
    evidence_type: EvidenceType
    relevance_score: float
    confidence_level: str
    supporting_explanation: str
    domain_authority: float
    page_quality_score: float
    last_validated: float
    
    # Diversity-specific fields
    diversity_score: float = 0.0
    source_tier: str = "unknown"
    uniqueness_factor: float = 0.0
    rotation_index: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'evidence_type': self.evidence_type.value if hasattr(self.evidence_type, 'value') else str(self.evidence_type),
            'relevance_score': self.relevance_score,
            'confidence_level': self.confidence_level,
            'supporting_explanation': self.supporting_explanation,
            'domain_authority': self.domain_authority,
            'page_quality_score': self.page_quality_score,
            'last_validated': self.last_validated,
            'diversity_score': self.diversity_score,
            'source_tier': self.source_tier,
            'uniqueness_factor': self.uniqueness_factor,
            'rotation_index': self.rotation_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedEvidenceURL':
        """Create from dictionary."""
        # Handle evidence_type conversion
        evidence_type = data.get('evidence_type', 'general_information')
        if isinstance(evidence_type, str):
            try:
                evidence_type = EvidenceType(evidence_type)
            except ValueError:
                evidence_type = EvidenceType.GENERAL_INFORMATION
        
        return cls(
            url=data.get('url', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            evidence_type=evidence_type,
            relevance_score=data.get('relevance_score', 0.0),
            confidence_level=data.get('confidence_level', 'low'),
            supporting_explanation=data.get('supporting_explanation', ''),
            domain_authority=data.get('domain_authority', 0.0),
            page_quality_score=data.get('page_quality_score', 0.0),
            last_validated=data.get('last_validated', 0.0),
            diversity_score=data.get('diversity_score', 0.0),
            source_tier=data.get('source_tier', 'unknown'),
            uniqueness_factor=data.get('uniqueness_factor', 0.0),
            rotation_index=data.get('rotation_index', 0)
        )


@dataclass
class DiversityConfig:
    """Configuration for diversity-focused processing."""
    # Core diversity settings
    ensure_url_uniqueness: bool = True
    max_same_domain_per_candidate: int = 1
    prioritize_alternatives: bool = True
    diversity_weight: float = 0.3
    
    # Source preferences
    max_major_sources_per_batch: int = 2
    min_alternative_sources: int = 3
    preferred_source_tiers: List[str] = field(default_factory=lambda: ["alternative", "niche", "mid-tier"])
    
    # Exclusion settings
    exclude_domains: Set[str] = field(default_factory=set)
    exclude_major_companies: bool = False
    
    # Processing settings
    enable_source_rotation: bool = True
    diversity_mode: str = "balanced"  # conservative, balanced, aggressive
    max_urls_per_candidate: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'ensure_url_uniqueness': self.ensure_url_uniqueness,
            'max_same_domain_per_candidate': self.max_same_domain_per_candidate,
            'prioritize_alternatives': self.prioritize_alternatives,
            'diversity_weight': self.diversity_weight,
            'max_major_sources_per_batch': self.max_major_sources_per_batch,
            'min_alternative_sources': self.min_alternative_sources,
            'preferred_source_tiers': self.preferred_source_tiers,
            'exclude_domains': list(self.exclude_domains),
            'exclude_major_companies': self.exclude_major_companies,
            'enable_source_rotation': self.enable_source_rotation,
            'diversity_mode': self.diversity_mode,
            'max_urls_per_candidate': self.max_urls_per_candidate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiversityConfig':
        """Create from dictionary."""
        return cls(
            ensure_url_uniqueness=data.get('ensure_url_uniqueness', True),
            max_same_domain_per_candidate=data.get('max_same_domain_per_candidate', 1),
            prioritize_alternatives=data.get('prioritize_alternatives', True),
            diversity_weight=data.get('diversity_weight', 0.3),
            max_major_sources_per_batch=data.get('max_major_sources_per_batch', 2),
            min_alternative_sources=data.get('min_alternative_sources', 3),
            preferred_source_tiers=data.get('preferred_source_tiers', ["alternative", "niche", "mid-tier"]),
            exclude_domains=set(data.get('exclude_domains', [])),
            exclude_major_companies=data.get('exclude_major_companies', False),
            enable_source_rotation=data.get('enable_source_rotation', True),
            diversity_mode=data.get('diversity_mode', 'balanced'),
            max_urls_per_candidate=data.get('max_urls_per_candidate', 5)
        )
    
    def save_to_file(self, filepath: str):
        """Save configuration to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'DiversityConfig':
        """Load configuration from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class ProcessingStats:
    """Statistics for diversity processing."""
    candidates_processed: int = 0
    urls_found: int = 0
    unique_domains: int = 0
    diversity_score: float = 0.0
    alternative_sources_used: int = 0
    major_sources_used: int = 0
    processing_time_total: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'candidates_processed': self.candidates_processed,
            'urls_found': self.urls_found,
            'unique_domains': self.unique_domains,
            'diversity_score': self.diversity_score,
            'alternative_sources_used': self.alternative_sources_used,
            'major_sources_used': self.major_sources_used,
            'processing_time_total': self.processing_time_total,
            'average_processing_time': self.processing_time_total / max(self.candidates_processed, 1),
            'average_urls_per_candidate': self.urls_found / max(self.candidates_processed, 1)
        }


@dataclass
class CandidateResult:
    """Result for a single candidate with enhanced evidence."""
    candidate_id: str
    original_candidate: Dict[str, Any]
    evidence_urls: List[EnhancedEvidenceURL]
    processing_time: float
    diversity_metrics: Dict[str, float]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        result = {
            **self.original_candidate,
            'evidence_urls': [url.to_dict() for url in self.evidence_urls],
            'evidence_processing_time': self.processing_time,
            'evidence_diversity_metrics': self.diversity_metrics
        }
        
        if self.error_message:
            result['evidence_error'] = self.error_message
        
        return result


@dataclass
class BatchResult:
    """Result for a batch of candidates."""
    candidate_results: List[CandidateResult]
    batch_stats: ProcessingStats
    diversity_analysis: Dict[str, Any]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'candidates': [result.to_dict() for result in self.candidate_results],
            'batch_statistics': self.batch_stats.to_dict(),
            'diversity_analysis': self.diversity_analysis,
            'recommendations': self.recommendations
        }


class ConfigurationManager:
    """Manages diversity configuration with presets and validation."""
    
    def __init__(self):
        self.presets = self._initialize_presets()
    
    def _initialize_presets(self) -> Dict[str, DiversityConfig]:
        """Initialize configuration presets."""
        return {
            'conservative': DiversityConfig(
                ensure_url_uniqueness=True,
                max_same_domain_per_candidate=2,
                prioritize_alternatives=False,
                diversity_weight=0.2,
                diversity_mode='conservative',
                exclude_major_companies=False
            ),
            
            'balanced': DiversityConfig(
                ensure_url_uniqueness=True,
                max_same_domain_per_candidate=1,
                prioritize_alternatives=True,
                diversity_weight=0.3,
                diversity_mode='balanced',
                exclude_major_companies=False
            ),
            
            'aggressive': DiversityConfig(
                ensure_url_uniqueness=True,
                max_same_domain_per_candidate=1,
                prioritize_alternatives=True,
                diversity_weight=0.5,
                diversity_mode='aggressive',
                exclude_major_companies=True,
                min_alternative_sources=4
            ),
            
            'maximum_diversity': DiversityConfig(
                ensure_url_uniqueness=True,
                max_same_domain_per_candidate=1,
                prioritize_alternatives=True,
                diversity_weight=0.7,
                diversity_mode='aggressive',
                exclude_major_companies=True,
                min_alternative_sources=5,
                max_major_sources_per_batch=1
            )
        }
    
    def get_preset(self, preset_name: str) -> DiversityConfig:
        """Get a configuration preset."""
        if preset_name not in self.presets:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(self.presets.keys())}")
        
        return self.presets[preset_name]
    
    def validate_config(self, config: DiversityConfig) -> List[str]:
        """Validate configuration and return any warnings."""
        warnings = []
        
        # Check diversity weight
        if config.diversity_weight < 0 or config.diversity_weight > 1:
            warnings.append("Diversity weight should be between 0 and 1")
        
        # Check domain limits
        if config.max_same_domain_per_candidate < 1:
            warnings.append("Max same domain per candidate should be at least 1")
        
        # Check URL limits
        if config.max_urls_per_candidate < 1:
            warnings.append("Max URLs per candidate should be at least 1")
        
        # Check source requirements
        if config.min_alternative_sources > config.max_urls_per_candidate:
            warnings.append("Min alternative sources cannot exceed max URLs per candidate")
        
        # Check diversity mode
        valid_modes = ['conservative', 'balanced', 'aggressive']
        if config.diversity_mode not in valid_modes:
            warnings.append(f"Diversity mode should be one of: {valid_modes}")
        
        return warnings
    
    def create_custom_config(
        self,
        base_preset: str = 'balanced',
        **overrides
    ) -> DiversityConfig:
        """Create a custom configuration based on a preset with overrides."""
        base_config = self.get_preset(base_preset)
        
        # Apply overrides
        config_dict = base_config.to_dict()
        config_dict.update(overrides)
        
        return DiversityConfig.from_dict(config_dict)


def serialize_evidence_urls(evidence_urls: List[EnhancedEvidenceURL]) -> List[Dict[str, Any]]:
    """Serialize evidence URLs for API responses."""
    return [url.to_dict() for url in evidence_urls]


def deserialize_evidence_urls(data: List[Dict[str, Any]]) -> List[EnhancedEvidenceURL]:
    """Deserialize evidence URLs from API data."""
    return [EnhancedEvidenceURL.from_dict(url_data) for url_data in data]


def create_enhanced_candidate_response(
    candidate: Dict[str, Any],
    evidence_urls: List[EnhancedEvidenceURL],
    processing_time: float,
    diversity_metrics: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """Create enhanced candidate response with diversity data."""
    diversity_metrics = diversity_metrics or {}
    
    enhanced_candidate = {
        **candidate,
        'evidence_urls': serialize_evidence_urls(evidence_urls),
        'evidence_processing_time': processing_time,
        'evidence_diversity_metrics': diversity_metrics,
        'evidence_summary': f"Found {len(evidence_urls)} diverse evidence URLs",
        'evidence_confidence': sum(url.relevance_score for url in evidence_urls) / max(len(evidence_urls), 1)
    }
    
    return enhanced_candidate


def test_enhanced_data_models():
    """Test function for enhanced data models."""
    print("Testing Enhanced Data Models:")
    print("=" * 50)
    
    # Test DiversityConfig
    print("1. Testing DiversityConfig:")
    config = DiversityConfig(
        diversity_weight=0.4,
        max_same_domain_per_candidate=1,
        exclude_domains={'example.com', 'test.com'}
    )
    
    print(f"   Original config: diversity_weight={config.diversity_weight}")
    
    # Test serialization
    config_dict = config.to_dict()
    print(f"   Serialized exclude_domains: {config_dict['exclude_domains']}")
    
    # Test deserialization
    restored_config = DiversityConfig.from_dict(config_dict)
    print(f"   Restored config: diversity_weight={restored_config.diversity_weight}")
    print(f"   Exclude domains match: {config.exclude_domains == restored_config.exclude_domains}")
    
    # Test ConfigurationManager
    print("\n2. Testing ConfigurationManager:")
    config_manager = ConfigurationManager()
    
    print(f"   Available presets: {list(config_manager.presets.keys())}")
    
    balanced_config = config_manager.get_preset('balanced')
    print(f"   Balanced preset diversity_weight: {balanced_config.diversity_weight}")
    
    # Test validation
    warnings = config_manager.validate_config(balanced_config)
    print(f"   Validation warnings for balanced preset: {len(warnings)}")
    
    # Test custom config
    custom_config = config_manager.create_custom_config(
        'balanced',
        diversity_weight=0.6,
        max_urls_per_candidate=3
    )
    print(f"   Custom config diversity_weight: {custom_config.diversity_weight}")
    print(f"   Custom config max_urls: {custom_config.max_urls_per_candidate}")
    
    # Test EnhancedEvidenceURL
    print("\n3. Testing EnhancedEvidenceURL:")
    evidence_url = EnhancedEvidenceURL(
        url="https://example.com/test",
        title="Test Page",
        description="Test description",
        evidence_type=EvidenceType.PRODUCT_PAGE,
        relevance_score=0.8,
        confidence_level="high",
        supporting_explanation="Test explanation",
        domain_authority=0.7,
        page_quality_score=0.9,
        last_validated=1234567890,
        diversity_score=0.6,
        source_tier="alternative"
    )
    
    # Test serialization
    url_dict = evidence_url.to_dict()
    print(f"   Serialized evidence_type: {url_dict['evidence_type']}")
    
    # Test deserialization
    restored_url = EnhancedEvidenceURL.from_dict(url_dict)
    print(f"   Restored URL: {restored_url.url}")
    print(f"   Evidence types match: {evidence_url.evidence_type == restored_url.evidence_type}")


if __name__ == '__main__':
    test_enhanced_data_models()