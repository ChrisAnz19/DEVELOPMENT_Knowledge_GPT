#!/usr/bin/env python3
"""
Evidence URL Data Models and Structures for URL Evidence Finder.

This module defines all the data models, enums, and structures used throughout
the URL Evidence Finder system, including validation and serialization methods.
"""

import json
import time
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pydantic import BaseModel, Field, field_validator, HttpUrl


class ClaimType(Enum):
    """Types of behavioral claims that can be extracted."""
    COMPANY_RESEARCH = "company_research"
    PRODUCT_EVALUATION = "product_evaluation"
    PRICING_RESEARCH = "pricing_research"
    FEATURE_COMPARISON = "feature_comparison"
    VENDOR_EVALUATION = "vendor_evaluation"
    MARKET_RESEARCH = "market_research"
    GENERAL_ACTIVITY = "general_activity"


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


class ConfidenceLevel(Enum):
    """Confidence levels for evidence quality."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Pydantic Models for API serialization and validation

class SearchableClaimModel(BaseModel):
    """Pydantic model for searchable claims."""
    text: str = Field(..., description="Original claim text")
    entities: Dict[str, List[str]] = Field(default_factory=dict, description="Extracted entities")
    claim_type: ClaimType = Field(..., description="Categorized claim type")
    priority: int = Field(..., ge=1, le=10, description="Search priority (1-10)")
    search_terms: List[str] = Field(default_factory=list, description="Key terms for searching")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in claim extraction")
    
    class Config:
        use_enum_values = True


class SearchQueryModel(BaseModel):
    """Pydantic model for search queries."""
    query: str = Field(..., description="The search query string")
    expected_domains: List[str] = Field(default_factory=list, description="Preferred domains")
    page_types: List[str] = Field(default_factory=list, description="Expected page types")
    priority: int = Field(..., ge=1, le=10, description="Query priority")
    claim_support: str = Field(..., description="How this query supports the claim")
    search_strategy: str = Field(..., description="Strategy used for this query")


class URLCandidateModel(BaseModel):
    """Pydantic model for URL candidates from search results."""
    url: HttpUrl = Field(..., description="The actual URL")
    title: str = Field(..., description="Page title")
    snippet: str = Field(default="", description="Content snippet/description")
    domain: str = Field(..., description="Domain name")
    page_type: Optional[str] = Field(None, description="Detected page type")
    search_query: str = Field(..., description="Query that found this URL")
    citation_index: int = Field(..., ge=0, description="Citation index from search results")
    
    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v):
        if not v or '.' not in v:
            raise ValueError('Invalid domain format')
        return v.lower()


class EvidenceURLModel(BaseModel):
    """Pydantic model for validated evidence URLs."""
    url: HttpUrl = Field(..., description="The actual URL")
    title: str = Field(..., description="Page title")
    description: str = Field(..., description="Brief description of relevance")
    evidence_type: EvidenceType = Field(..., description="Category of evidence")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence level")
    supporting_explanation: str = Field(..., description="How this URL supports the claim")
    domain_authority: float = Field(..., ge=0.0, le=1.0, description="Domain authority score")
    page_quality_score: float = Field(..., ge=0.0, le=1.0, description="Page quality score")
    last_validated: float = Field(default_factory=time.time, description="Validation timestamp")
    
    class Config:
        use_enum_values = True
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters long')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters long')
        return v.strip()


class SearchResultModel(BaseModel):
    """Pydantic model for search results."""
    query: SearchQueryModel = Field(..., description="Original search query")
    urls: List[URLCandidateModel] = Field(default_factory=list, description="Found URL candidates")
    citations: List[Dict[str, Any]] = Field(default_factory=list, description="Raw citation data")
    search_metadata: Dict[str, Any] = Field(default_factory=dict, description="Search metadata")
    success: bool = Field(..., description="Whether search was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    execution_time: Optional[float] = Field(None, description="Search execution time in seconds")


class CandidateEvidenceModel(BaseModel):
    """Pydantic model for complete candidate evidence."""
    candidate_id: str = Field(..., description="Unique candidate identifier")
    original_explanations: List[str] = Field(..., description="Original behavioral explanations")
    evidence_urls: List[EvidenceURLModel] = Field(default_factory=list, description="Evidence URLs")
    search_metadata: Dict[str, Any] = Field(default_factory=dict, description="Search process metadata")
    processing_time: Optional[float] = Field(None, description="Total processing time")
    success: bool = Field(default=True, description="Whether evidence gathering was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    @field_validator('candidate_id')
    @classmethod
    def validate_candidate_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Candidate ID cannot be empty')
        return v.strip()
    
    @field_validator('original_explanations')
    @classmethod
    def validate_explanations(cls, v):
        if not v:
            raise ValueError('At least one explanation is required')
        return [exp.strip() for exp in v if exp.strip()]


class EnhancedCandidateModel(BaseModel):
    """Pydantic model for enhanced candidate with evidence URLs."""
    # Original candidate fields
    id: Union[str, int] = Field(..., description="Candidate ID")
    name: str = Field(..., description="Candidate name")
    title: Optional[str] = Field(None, description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    location: Optional[str] = Field(None, description="Location")
    reasons: List[str] = Field(default_factory=list, description="Behavioral explanations")
    
    # Enhanced evidence fields
    evidence_urls: List[EvidenceURLModel] = Field(default_factory=list, description="Supporting evidence URLs")
    evidence_summary: Optional[str] = Field(None, description="Summary of evidence found")
    evidence_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall evidence confidence")
    evidence_processing_time: Optional[float] = Field(None, description="Evidence processing time")
    
    class Config:
        use_enum_values = True
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


# Dataclass models for internal processing (lighter weight)

@dataclass
class SearchableClaim:
    """Dataclass for searchable claims (internal processing)."""
    text: str
    entities: Dict[str, List[str]]
    claim_type: ClaimType
    priority: int
    search_terms: List[str]
    confidence: float
    
    def to_model(self) -> SearchableClaimModel:
        """Convert to Pydantic model."""
        return SearchableClaimModel(**asdict(self))
    
    @classmethod
    def from_model(cls, model: SearchableClaimModel) -> 'SearchableClaim':
        """Create from Pydantic model."""
        return cls(
            text=model.text,
            entities=model.entities,
            claim_type=model.claim_type,
            priority=model.priority,
            search_terms=model.search_terms,
            confidence=model.confidence
        )


@dataclass
class SearchQuery:
    """Dataclass for search queries (internal processing)."""
    query: str
    expected_domains: List[str]
    page_types: List[str]
    priority: int
    claim_support: str
    search_strategy: str
    
    def to_model(self) -> SearchQueryModel:
        """Convert to Pydantic model."""
        return SearchQueryModel(**asdict(self))


@dataclass
class URLCandidate:
    """Dataclass for URL candidates (internal processing)."""
    url: str
    title: str
    snippet: str
    domain: str
    page_type: Optional[str]
    search_query: str
    citation_index: int
    
    def to_model(self) -> URLCandidateModel:
        """Convert to Pydantic model."""
        return URLCandidateModel(**asdict(self))


@dataclass
class EvidenceURL:
    """Dataclass for evidence URLs (internal processing)."""
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
    
    def to_model(self) -> EvidenceURLModel:
        """Convert to Pydantic model."""
        return EvidenceURLModel(
            url=self.url,
            title=self.title,
            description=self.description,
            evidence_type=self.evidence_type,
            relevance_score=self.relevance_score,
            confidence_level=ConfidenceLevel(self.confidence_level),
            supporting_explanation=self.supporting_explanation,
            domain_authority=self.domain_authority,
            page_quality_score=self.page_quality_score,
            last_validated=self.last_validated
        )


@dataclass
class SearchResult:
    """Dataclass for search results (internal processing)."""
    query: SearchQuery
    urls: List[URLCandidate]
    citations: List[Dict[str, Any]]
    search_metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str]
    
    def to_model(self) -> SearchResultModel:
        """Convert to Pydantic model."""
        return SearchResultModel(
            query=self.query.to_model(),
            urls=[url.to_model() for url in self.urls],
            citations=self.citations,
            search_metadata=self.search_metadata,
            success=self.success,
            error_message=self.error_message
        )


# Utility functions for model conversion and serialization

def serialize_evidence_urls(evidence_urls: List[EvidenceURL]) -> List[Dict[str, Any]]:
    """Serialize evidence URLs to dictionary format for API responses."""
    serialized = []
    for url in evidence_urls:
        model_dict = url.to_model().model_dump()
        # Convert HttpUrl to string for JSON serialization
        if 'url' in model_dict and hasattr(model_dict['url'], '__str__'):
            model_dict['url'] = str(model_dict['url'])
        serialized.append(model_dict)
    return serialized


def deserialize_evidence_urls(data: List[Dict[str, Any]]) -> List[EvidenceURL]:
    """Deserialize evidence URLs from dictionary format."""
    evidence_urls = []
    for item in data:
        model = EvidenceURLModel(**item)
        evidence_url = EvidenceURL(
            url=str(model.url),
            title=model.title,
            description=model.description,
            evidence_type=model.evidence_type,
            relevance_score=model.relevance_score,
            confidence_level=model.confidence_level.value,
            supporting_explanation=model.supporting_explanation,
            domain_authority=model.domain_authority,
            page_quality_score=model.page_quality_score,
            last_validated=model.last_validated
        )
        evidence_urls.append(evidence_url)
    return evidence_urls


def create_enhanced_candidate_response(
    candidate: Dict[str, Any],
    evidence_urls: List[EvidenceURL],
    processing_time: Optional[float] = None
) -> Dict[str, Any]:
    """Create enhanced candidate response with evidence URLs."""
    # Calculate evidence summary and confidence
    evidence_summary = _generate_evidence_summary(evidence_urls)
    evidence_confidence = _calculate_overall_confidence(evidence_urls)
    
    # Create enhanced response
    enhanced_candidate = {
        **candidate,  # Original candidate fields
        'evidence_urls': serialize_evidence_urls(evidence_urls),
        'evidence_summary': evidence_summary,
        'evidence_confidence': evidence_confidence,
        'evidence_processing_time': processing_time
    }
    
    return enhanced_candidate


def _generate_evidence_summary(evidence_urls: List[EvidenceURL]) -> str:
    """Generate a summary of evidence found."""
    if not evidence_urls:
        return "No supporting evidence URLs found"
    
    count = len(evidence_urls)
    high_confidence = sum(1 for url in evidence_urls if url.confidence_level == "high")
    
    # Count evidence types
    type_counts = {}
    for url in evidence_urls:
        type_name = url.evidence_type.value.replace('_', ' ').title()
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    # Build summary
    summary_parts = [f"Found {count} supporting URL{'s' if count != 1 else ''}"]
    
    if high_confidence > 0:
        summary_parts.append(f"{high_confidence} high-confidence source{'s' if high_confidence != 1 else ''}")
    
    if type_counts:
        top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:2]
        type_desc = ", ".join([f"{name} ({count})" for name, count in top_types])
        summary_parts.append(f"including {type_desc}")
    
    return " ".join(summary_parts)


def _calculate_overall_confidence(evidence_urls: List[EvidenceURL]) -> float:
    """Calculate overall confidence score for evidence set."""
    if not evidence_urls:
        return 0.0
    
    # Weight by relevance score and confidence level
    total_weighted_score = 0.0
    total_weight = 0.0
    
    confidence_weights = {"high": 1.0, "medium": 0.7, "low": 0.4}
    
    for url in evidence_urls:
        weight = confidence_weights.get(url.confidence_level, 0.5)
        weighted_score = url.relevance_score * weight
        total_weighted_score += weighted_score
        total_weight += weight
    
    return total_weighted_score / total_weight if total_weight > 0 else 0.0


def validate_candidate_for_evidence_processing(candidate: Dict[str, Any]) -> bool:
    """Validate that candidate has required fields for evidence processing."""
    required_fields = ['id', 'name']
    explanation_fields = ['reasons', 'behavioral_data', 'accuracy_explanation']
    
    # Check required fields
    for field in required_fields:
        if field not in candidate:
            return False
    
    # Check for at least one explanation field
    has_explanations = any(
        field in candidate and candidate[field] 
        for field in explanation_fields
    )
    
    return has_explanations


def extract_explanations_from_candidate(candidate: Dict[str, Any]) -> List[str]:
    """Extract all explanation text from candidate object."""
    explanations = []
    
    # Extract from reasons field
    reasons = candidate.get('reasons', [])
    if isinstance(reasons, list):
        explanations.extend([str(reason) for reason in reasons if reason])
    elif isinstance(reasons, str) and reasons.strip():
        explanations.append(reasons.strip())
    
    # Extract from behavioral_data
    behavioral_data = candidate.get('behavioral_data', {})
    if isinstance(behavioral_data, dict):
        for key in ['explanation', 'activity_explanation', 'research_explanation']:
            if key in behavioral_data and behavioral_data[key]:
                explanations.append(str(behavioral_data[key]))
    
    # Extract from accuracy_explanation
    accuracy_explanation = candidate.get('accuracy_explanation', '')
    if accuracy_explanation and accuracy_explanation.strip():
        explanations.append(accuracy_explanation.strip())
    
    return [exp for exp in explanations if exp.strip()]


def test_evidence_models():
    """Test function for evidence models."""
    print("Testing Evidence Models:")
    print("=" * 50)
    
    # Test SearchableClaim
    claim = SearchableClaim(
        text="Researching Salesforce pricing options",
        entities={'companies': ['salesforce'], 'pricing_terms': ['pricing']},
        claim_type=ClaimType.PRICING_RESEARCH,
        priority=8,
        search_terms=['salesforce', 'pricing'],
        confidence=0.9
    )
    
    claim_model = claim.to_model()
    print(f"Claim Model: {claim_model.model_dump()}")
    
    # Test EvidenceURL
    evidence = EvidenceURL(
        url="https://salesforce.com/pricing",
        title="Salesforce Pricing",
        description="Official pricing information",
        evidence_type=EvidenceType.PRICING_PAGE,
        relevance_score=0.95,
        confidence_level="high",
        supporting_explanation="Supports pricing research claim",
        domain_authority=0.95,
        page_quality_score=0.9,
        last_validated=time.time()
    )
    
    evidence_model = evidence.to_model()
    print(f"\nEvidence Model: {evidence_model.model_dump()}")
    
    # Test serialization
    serialized = serialize_evidence_urls([evidence])
    print(f"\nSerialized Evidence: {json.dumps(serialized, indent=2)}")
    
    # Test candidate validation
    test_candidate = {
        'id': '123',
        'name': 'John Doe',
        'reasons': ['Researching CRM solutions']
    }
    
    is_valid = validate_candidate_for_evidence_processing(test_candidate)
    explanations = extract_explanations_from_candidate(test_candidate)
    
    print(f"\nCandidate Valid: {is_valid}")
    print(f"Extracted Explanations: {explanations}")


if __name__ == '__main__':
    test_evidence_models()