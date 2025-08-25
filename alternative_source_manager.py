#!/usr/bin/env python3
"""
Alternative Source Manager for URL Diversity Enhancement.

This module manages discovery and rotation of alternative/diverse sources
to ensure varied URL evidence across candidates.
"""

import random
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SourceTier(Enum):
    """Classification of source tiers by market presence."""
    MAJOR = "major"           # Fortune 500, market leaders
    MID_TIER = "mid-tier"     # Established mid-market players
    NICHE = "niche"           # Specialized/boutique solutions
    ALTERNATIVE = "alternative"  # Lesser-known but legitimate options
    EMERGING = "emerging"     # Startups and new entrants


@dataclass
class AlternativeSource:
    """Represents an alternative source for evidence."""
    name: str
    domain: str
    category: str
    tier: SourceTier
    keywords: List[str]
    description: str
    confidence_score: float = 0.8  # How confident we are this is a good alternative


class AlternativeSourceManager:
    """
    Manages discovery and rotation of alternative/diverse sources
    to provide varied evidence across candidates.
    """
    
    def __init__(self):
        # Initialize alternative companies database
        self.alternative_companies = self._initialize_alternative_companies()
        
        # Niche and specialized sources
        self.niche_sources = self._initialize_niche_sources()
        
        # Rotation state tracking
        self.rotation_counters = {}
        self.used_sources_per_category = {}
        
        # Category mappings for claim analysis
        self.category_keywords = self._initialize_category_keywords()
        
        # Major companies to avoid/deprioritize
        self.major_companies = self._initialize_major_companies()
    
    def get_alternative_companies(
        self,
        category: str,
        exclude: Set[str] = None,
        count: int = 3,
        tier_preference: List[SourceTier] = None
    ) -> List[AlternativeSource]:
        """
        Get alternative companies for a specific category.
        
        Args:
            category: Product/service category
            exclude: Company names/domains to exclude
            count: Number of alternatives to return
            tier_preference: Preferred source tiers in order
            
        Returns:
            List of alternative sources
        """
        exclude = exclude or set()
        tier_preference = tier_preference or [SourceTier.ALTERNATIVE, SourceTier.NICHE, SourceTier.MID_TIER]
        
        # Get all sources for category
        category_sources = self.alternative_companies.get(category, [])
        
        # Filter out excluded sources
        available_sources = [
            source for source in category_sources
            if source.name.lower() not in {e.lower() for e in exclude}
            and source.domain.lower() not in {e.lower() for e in exclude}
        ]
        
        if not available_sources:
            return []
        
        # Sort by tier preference and confidence
        def sort_key(source):
            tier_priority = 0
            if source.tier in tier_preference:
                tier_priority = len(tier_preference) - tier_preference.index(source.tier)
            return (tier_priority, source.confidence_score)
        
        available_sources.sort(key=sort_key, reverse=True)
        
        # Apply rotation to ensure variety across candidates
        rotated_sources = self._apply_rotation(available_sources, category)
        
        return rotated_sources[:count]
    
    def identify_category_from_claim(self, claim_text: str, entities: Dict[str, List[str]]) -> Optional[str]:
        """
        Identify product category from claim text and entities.
        
        Args:
            claim_text: Text of the behavioral claim
            entities: Extracted entities (companies, products, activities)
            
        Returns:
            Identified category or None
        """
        claim_lower = claim_text.lower()
        
        # Priority check for real estate terms (most specific first)
        real_estate_terms = [
            'real estate', 'property', 'properties', 'listing', 'listings',
            'home', 'homes', 'house', 'houses', 'mansion', 'mansions',
            'estate', 'residential', 'luxury home', 'greenwich', 'westchester',
            'mls', 'realtor', 'realty', 'brokerage', 'agent', 'broker'
        ]
        if any(term in claim_lower for term in real_estate_terms):
            return 'real_estate'
        
        # Check for financial services
        financial_terms = [
            'mortgage', 'loan', 'lending', 'financing', 'calculator',
            'rate', 'rates', 'banking', 'financial', 'pre-approval',
            'refinancing', 'credit', 'debt', 'wealth management'
        ]
        if any(term in claim_lower for term in financial_terms):
            return 'financial_services'
        
        # Check for investment forums/communities
        investment_terms = [
            'investment', 'investing', 'investor', 'forum', 'forums',
            'community', 'discussion', 'networking', 'club', 'portfolio'
        ]
        if any(term in claim_lower for term in investment_terms):
            return 'investment_forums'
        
        # Check products from entities
        products = entities.get('products', [])
        for product in products:
            product_lower = product.lower()
            for category, keywords in self.category_keywords.items():
                if any(keyword in product_lower for keyword in keywords):
                    return category
        
        # Check claim text for category keywords
        for category, keywords in self.category_keywords.items():
            if any(keyword in claim_lower for keyword in keywords):
                return category
        
        # Check activities for category hints
        activities = entities.get('activities', [])
        for activity in activities:
            activity_lower = activity.lower()
            if 'crm' in activity_lower or 'customer' in activity_lower:
                return 'crm'
            elif 'marketing' in activity_lower:
                return 'marketing_automation'
            elif 'project' in activity_lower or 'task' in activity_lower:
                return 'project_management'
        
        return None
    
    def get_niche_sources(
        self,
        category: str,
        search_terms: List[str],
        exclude: Set[str] = None,
        count: int = 2
    ) -> List[AlternativeSource]:
        """
        Get niche/specialized sources for a category.
        
        Args:
            category: Product category
            search_terms: Terms from the original claim
            exclude: Sources to exclude
            count: Number of sources to return
            
        Returns:
            List of niche sources
        """
        exclude = exclude or set()
        
        # Get niche sources for category
        niche_sources = self.niche_sources.get(category, [])
        
        # Filter and score by relevance to search terms
        scored_sources = []
        for source in niche_sources:
            if (source.name.lower() not in {e.lower() for e in exclude} and
                source.domain.lower() not in {e.lower() for e in exclude}):
                
                # Calculate relevance score
                relevance = self._calculate_source_relevance(source, search_terms)
                scored_sources.append((source, relevance))
        
        # Sort by relevance and confidence
        scored_sources.sort(key=lambda x: (x[1], x[0].confidence_score), reverse=True)
        
        return [source for source, _ in scored_sources[:count]]
    
    def rotate_source_selection(
        self,
        available_sources: List[AlternativeSource],
        category: str,
        candidate_index: int = None
    ) -> List[AlternativeSource]:
        """
        Apply rotation to source selection for variety across candidates.
        
        Args:
            available_sources: Available sources to choose from
            category: Product category
            candidate_index: Index of current candidate (for deterministic rotation)
            
        Returns:
            Rotated source selection
        """
        if not available_sources:
            return []
        
        # Use candidate index for deterministic rotation if provided
        if candidate_index is not None:
            rotation_offset = candidate_index % len(available_sources)
        else:
            # Use internal counter for rotation
            if category not in self.rotation_counters:
                self.rotation_counters[category] = 0
            rotation_offset = self.rotation_counters[category]
            self.rotation_counters[category] = (self.rotation_counters[category] + 1) % len(available_sources)
        
        # Rotate the list
        rotated = available_sources[rotation_offset:] + available_sources[:rotation_offset]
        
        return rotated
    
    def is_major_company(self, company_name: str) -> bool:
        """
        Check if a company is considered a major player.
        
        Args:
            company_name: Name of the company
            
        Returns:
            True if company is a major player
        """
        return company_name.lower() in {c.lower() for c in self.major_companies}
    
    def get_exclusion_terms_for_diversity(self, category: str) -> List[str]:
        """
        Get terms to exclude in searches to promote diversity.
        
        Args:
            category: Product category
            
        Returns:
            List of terms to exclude (major company names)
        """
        exclusion_terms = []
        
        # Add major companies for this category
        category_sources = self.alternative_companies.get(category, [])
        major_sources = [s for s in category_sources if s.tier == SourceTier.MAJOR]
        
        for source in major_sources:
            exclusion_terms.append(f"-{source.name}")
            exclusion_terms.append(f"-site:{source.domain}")
        
        # Add general major companies
        exclusion_terms.extend([
            "-salesforce", "-hubspot", "-microsoft", "-google",
            "-amazon", "-oracle", "-sap", "-adobe"
        ])
        
        return exclusion_terms
    
    def _apply_rotation(self, sources: List[AlternativeSource], category: str) -> List[AlternativeSource]:
        """Apply rotation logic to ensure variety."""
        return self.rotate_source_selection(sources, category)
    
    def _calculate_source_relevance(self, source: AlternativeSource, search_terms: List[str]) -> float:
        """Calculate how relevant a source is to the search terms."""
        if not search_terms:
            return source.confidence_score
        
        # Check keyword matches
        source_keywords = [kw.lower() for kw in source.keywords]
        search_terms_lower = [term.lower() for term in search_terms]
        
        matches = 0
        for term in search_terms_lower:
            if any(term in keyword for keyword in source_keywords):
                matches += 1
        
        # Calculate relevance score
        relevance = matches / len(search_terms) if search_terms else 0
        
        # Combine with confidence score
        return (relevance * 0.7) + (source.confidence_score * 0.3)
    
    def _initialize_alternative_companies(self) -> Dict[str, List[AlternativeSource]]:
        """Initialize the alternative companies database."""
        return {
            'real_estate': [
                AlternativeSource("Zillow", "zillow.com", "real_estate", SourceTier.MAJOR,
                                ["real estate", "property", "listings"], "Real estate marketplace", 0.9),
                AlternativeSource("Realtor.com", "realtor.com", "real_estate", SourceTier.MAJOR,
                                ["real estate", "mls", "listings"], "MLS real estate listings", 0.9),
                AlternativeSource("Redfin", "redfin.com", "real_estate", SourceTier.MID_TIER,
                                ["real estate", "brokerage", "listings"], "Real estate brokerage", 0.8),
                AlternativeSource("Compass", "compass.com", "real_estate", SourceTier.MID_TIER,
                                ["luxury", "real estate", "agent"], "Luxury real estate platform", 0.8),
                AlternativeSource("Sotheby's Realty", "sothebysrealty.com", "real_estate", SourceTier.NICHE,
                                ["luxury", "international", "real estate"], "Luxury international real estate", 0.9),
                AlternativeSource("Christie's Real Estate", "christiesrealestate.com", "real_estate", SourceTier.NICHE,
                                ["luxury", "auction", "real estate"], "Luxury real estate auctions", 0.8),
                AlternativeSource("Mansion Global", "mansionglobal.com", "real_estate", SourceTier.ALTERNATIVE,
                                ["luxury", "mansion", "global"], "Luxury property news and listings", 0.7),
                AlternativeSource("LuxuryRealEstate.com", "luxuryrealestate.com", "real_estate", SourceTier.NICHE,
                                ["luxury", "high-end", "properties"], "High-end luxury properties", 0.7),
            ],
            'financial_services': [
                AlternativeSource("Bankrate", "bankrate.com", "financial_services", SourceTier.MID_TIER,
                                ["mortgage", "rates", "calculator"], "Financial rates and calculators", 0.8),
                AlternativeSource("NerdWallet", "nerdwallet.com", "financial_services", SourceTier.MID_TIER,
                                ["personal finance", "mortgage", "calculator"], "Personal finance advice", 0.8),
                AlternativeSource("Quicken Loans", "quickenloans.com", "financial_services", SourceTier.MID_TIER,
                                ["mortgage", "lending", "online"], "Online mortgage lending", 0.8),
                AlternativeSource("LendingTree", "lendingtree.com", "financial_services", SourceTier.ALTERNATIVE,
                                ["mortgage", "comparison", "lending"], "Mortgage comparison platform", 0.7),
                AlternativeSource("Rocket Mortgage", "rocketmortgage.com", "financial_services", SourceTier.MID_TIER,
                                ["mortgage", "digital", "application"], "Digital mortgage platform", 0.8),
            ],
            'investment_forums': [
                AlternativeSource("BiggerPockets", "biggerpockets.com", "investment_forums", SourceTier.ALTERNATIVE,
                                ["real estate", "investment", "community"], "Real estate investment community", 0.8),
                AlternativeSource("REI Club", "reiclub.com", "investment_forums", SourceTier.NICHE,
                                ["real estate", "investment", "club"], "Real estate investment club", 0.7),
                AlternativeSource("Connected Investors", "connectedinvestors.com", "investment_forums", SourceTier.NICHE,
                                ["real estate", "networking", "investors"], "Real estate investor network", 0.6),
            ],
            'crm': [
                AlternativeSource("Pipedrive", "pipedrive.com", "crm", SourceTier.ALTERNATIVE,
                                ["sales", "pipeline", "crm"], "Sales-focused CRM platform", 0.9),
                AlternativeSource("Freshworks", "freshworks.com", "crm", SourceTier.MID_TIER,
                                ["customer", "support", "crm"], "Customer experience platform", 0.8),
                AlternativeSource("Zoho CRM", "zoho.com", "crm", SourceTier.ALTERNATIVE,
                                ["business", "crm", "suite"], "Business software suite", 0.8),
                AlternativeSource("Insightly", "insightly.com", "crm", SourceTier.NICHE,
                                ["project", "crm", "small business"], "CRM for small businesses", 0.7),
                AlternativeSource("Copper", "copper.com", "crm", SourceTier.ALTERNATIVE,
                                ["google", "crm", "integration"], "Google Workspace CRM", 0.8),
                AlternativeSource("Airtable", "airtable.com", "crm", SourceTier.ALTERNATIVE,
                                ["database", "collaboration", "flexible"], "Flexible database platform", 0.7),
                AlternativeSource("Monday.com", "monday.com", "crm", SourceTier.MID_TIER,
                                ["work", "management", "collaboration"], "Work management platform", 0.8),
                AlternativeSource("ClickUp", "clickup.com", "crm", SourceTier.ALTERNATIVE,
                                ["productivity", "project", "all-in-one"], "All-in-one productivity", 0.7),
            ],
            
            'marketing_automation': [
                AlternativeSource("Mailchimp", "mailchimp.com", "marketing_automation", SourceTier.MID_TIER,
                                ["email", "marketing", "automation"], "Email marketing platform", 0.9),
                AlternativeSource("Constant Contact", "constantcontact.com", "marketing_automation", SourceTier.ALTERNATIVE,
                                ["email", "marketing", "small business"], "Small business marketing", 0.8),
                AlternativeSource("SendinBlue", "sendinblue.com", "marketing_automation", SourceTier.ALTERNATIVE,
                                ["email", "sms", "marketing"], "Email and SMS marketing", 0.8),
                AlternativeSource("ActiveCampaign", "activecampaign.com", "marketing_automation", SourceTier.ALTERNATIVE,
                                ["email", "automation", "crm"], "Email marketing with CRM", 0.8),
                AlternativeSource("Drip", "drip.com", "marketing_automation", SourceTier.NICHE,
                                ["ecommerce", "email", "automation"], "Ecommerce email marketing", 0.7),
                AlternativeSource("ConvertKit", "convertkit.com", "marketing_automation", SourceTier.NICHE,
                                ["creator", "email", "marketing"], "Creator-focused email marketing", 0.7),
                AlternativeSource("GetResponse", "getresponse.com", "marketing_automation", SourceTier.ALTERNATIVE,
                                ["email", "marketing", "webinar"], "Email marketing with webinars", 0.7),
            ],
            
            'project_management': [
                AlternativeSource("Smartsheet", "smartsheet.com", "project_management", SourceTier.MID_TIER,
                                ["spreadsheet", "project", "collaboration"], "Spreadsheet-based project management", 0.8),
                AlternativeSource("Wrike", "wrike.com", "project_management", SourceTier.ALTERNATIVE,
                                ["project", "collaboration", "enterprise"], "Enterprise project management", 0.8),
                AlternativeSource("Teamwork", "teamwork.com", "project_management", SourceTier.ALTERNATIVE,
                                ["project", "team", "collaboration"], "Team collaboration platform", 0.7),
                AlternativeSource("ProofHub", "proofhub.com", "project_management", SourceTier.NICHE,
                                ["project", "proofing", "collaboration"], "Project management with proofing", 0.7),
                AlternativeSource("Clarizen", "clarizen.com", "project_management", SourceTier.NICHE,
                                ["enterprise", "project", "portfolio"], "Enterprise project portfolio", 0.7),
                AlternativeSource("Workfront", "workfront.com", "project_management", SourceTier.MID_TIER,
                                ["enterprise", "marketing", "project"], "Enterprise work management", 0.8),
                AlternativeSource("LiquidPlanner", "liquidplanner.com", "project_management", SourceTier.NICHE,
                                ["predictive", "project", "scheduling"], "Predictive project management", 0.7),
            ],
            
            'communication': [
                AlternativeSource("Discord", "discord.com", "communication", SourceTier.ALTERNATIVE,
                                ["chat", "voice", "community"], "Community communication platform", 0.8),
                AlternativeSource("Mattermost", "mattermost.com", "communication", SourceTier.NICHE,
                                ["open source", "chat", "enterprise"], "Open source team messaging", 0.7),
                AlternativeSource("Rocket.Chat", "rocket.chat", "communication", SourceTier.NICHE,
                                ["open source", "chat", "customizable"], "Open source communication", 0.7),
                AlternativeSource("Flock", "flock.com", "communication", SourceTier.ALTERNATIVE,
                                ["team", "chat", "collaboration"], "Team communication platform", 0.6),
                AlternativeSource("Chanty", "chanty.com", "communication", SourceTier.NICHE,
                                ["simple", "team", "chat"], "Simple team chat", 0.6),
                AlternativeSource("Ryver", "ryver.com", "communication", SourceTier.NICHE,
                                ["team", "collaboration", "organization"], "Team collaboration platform", 0.6),
                AlternativeSource("Twist", "twist.com", "communication", SourceTier.NICHE,
                                ["asynchronous", "team", "communication"], "Asynchronous team communication", 0.7),
            ],
            
            'analytics': [
                AlternativeSource("Mixpanel", "mixpanel.com", "analytics", SourceTier.MID_TIER,
                                ["product", "analytics", "events"], "Product analytics platform", 0.8),
                AlternativeSource("Amplitude", "amplitude.com", "analytics", SourceTier.MID_TIER,
                                ["product", "analytics", "behavioral"], "Behavioral analytics platform", 0.8),
                AlternativeSource("Heap", "heap.io", "analytics", SourceTier.ALTERNATIVE,
                                ["automatic", "analytics", "capture"], "Automatic event capture", 0.7),
                AlternativeSource("FullStory", "fullstory.com", "analytics", SourceTier.ALTERNATIVE,
                                ["session", "replay", "analytics"], "Session replay and analytics", 0.8),
                AlternativeSource("Hotjar", "hotjar.com", "analytics", SourceTier.ALTERNATIVE,
                                ["heatmap", "user", "behavior"], "User behavior analytics", 0.8),
                AlternativeSource("Crazy Egg", "crazyegg.com", "analytics", SourceTier.NICHE,
                                ["heatmap", "optimization", "testing"], "Website optimization tools", 0.7),
                AlternativeSource("Kissmetrics", "kissmetrics.io", "analytics", SourceTier.NICHE,
                                ["customer", "analytics", "retention"], "Customer analytics platform", 0.7),
            ],
            
            'ecommerce': [
                AlternativeSource("BigCommerce", "bigcommerce.com", "ecommerce", SourceTier.MID_TIER,
                                ["ecommerce", "platform", "enterprise"], "Enterprise ecommerce platform", 0.8),
                AlternativeSource("WooCommerce", "woocommerce.com", "ecommerce", SourceTier.ALTERNATIVE,
                                ["wordpress", "ecommerce", "plugin"], "WordPress ecommerce plugin", 0.8),
                AlternativeSource("Magento", "magento.com", "ecommerce", SourceTier.MID_TIER,
                                ["ecommerce", "platform", "flexible"], "Flexible ecommerce platform", 0.7),
                AlternativeSource("PrestaShop", "prestashop.com", "ecommerce", SourceTier.ALTERNATIVE,
                                ["open source", "ecommerce", "free"], "Open source ecommerce", 0.7),
                AlternativeSource("OpenCart", "opencart.com", "ecommerce", SourceTier.NICHE,
                                ["open source", "simple", "ecommerce"], "Simple ecommerce solution", 0.6),
                AlternativeSource("Volusion", "volusion.com", "ecommerce", SourceTier.NICHE,
                                ["ecommerce", "all-in-one", "hosting"], "All-in-one ecommerce solution", 0.6),
            ]
        }
    
    def _initialize_niche_sources(self) -> Dict[str, List[AlternativeSource]]:
        """Initialize niche and specialized sources."""
        return {
            'crm': [
                AlternativeSource("Nutshell", "nutshell.com", "crm", SourceTier.NICHE,
                                ["simple", "crm", "small business"], "Simple CRM for small teams", 0.7),
                AlternativeSource("Capsule", "capsulecrm.com", "crm", SourceTier.NICHE,
                                ["simple", "contact", "management"], "Simple contact management", 0.6),
                AlternativeSource("Streak", "streak.com", "crm", SourceTier.NICHE,
                                ["gmail", "crm", "integration"], "Gmail-integrated CRM", 0.7),
            ],
            'marketing_automation': [
                AlternativeSource("Omnisend", "omnisend.com", "marketing_automation", SourceTier.NICHE,
                                ["ecommerce", "omnichannel", "automation"], "Ecommerce marketing automation", 0.7),
                AlternativeSource("Klaviyo", "klaviyo.com", "marketing_automation", SourceTier.ALTERNATIVE,
                                ["ecommerce", "email", "sms"], "Ecommerce email and SMS", 0.8),
                AlternativeSource("Pardot", "pardot.com", "marketing_automation", SourceTier.MID_TIER,
                                ["b2b", "marketing", "automation"], "B2B marketing automation", 0.8),
            ]
        }
    
    def _initialize_category_keywords(self) -> Dict[str, List[str]]:
        """Initialize category keyword mappings."""
        return {
            'real_estate': ['real estate', 'property', 'luxury', 'mansion', 'listing', 'home', 'house', 'estate', 'residential'],
            'financial_services': ['mortgage', 'loan', 'financing', 'calculator', 'rate', 'banking', 'financial'],
            'investment_forums': ['investment', 'forum', 'community', 'investor', 'discussion', 'property investment'],
            'crm': ['crm', 'customer relationship', 'sales management', 'lead management', 'contact management'],
            'marketing_automation': ['marketing automation', 'email marketing', 'campaign', 'nurturing', 'drip campaign'],
            'project_management': ['project management', 'task management', 'collaboration', 'workflow', 'project tracking'],
            'communication': ['communication', 'chat', 'messaging', 'team communication', 'collaboration'],
            'analytics': ['analytics', 'tracking', 'metrics', 'data analysis', 'reporting'],
            'ecommerce': ['ecommerce', 'online store', 'shopping cart', 'e-commerce', 'online retail'],
            'hr': ['hr', 'human resources', 'payroll', 'employee management', 'recruiting'],
            'accounting': ['accounting', 'bookkeeping', 'financial', 'invoicing', 'expense'],
            'cybersecurity': ['security', 'cybersecurity', 'antivirus', 'protection', 'firewall'],
            'cloud_storage': ['storage', 'file sharing', 'backup', 'cloud storage', 'document management']
        }
    
    def _initialize_major_companies(self) -> List[str]:
        """Initialize list of major companies to avoid for diversity."""
        return [
            'Salesforce', 'HubSpot', 'Microsoft', 'Google', 'Amazon', 'Oracle', 'SAP', 'Adobe',
            'Zoom', 'Slack', 'Shopify', 'Stripe', 'Twilio', 'Zendesk', 'Atlassian', 'ServiceNow',
            'Workday', 'Okta', 'Tableau', 'Snowflake', 'Databricks', 'MongoDB', 'DocuSign',
            'Box', 'Dropbox', 'Asana', 'Trello', 'Notion'
        ]


def test_alternative_source_manager():
    """Test function for the Alternative Source Manager."""
    print("Testing Alternative Source Manager:")
    print("=" * 50)
    
    # Create manager
    manager = AlternativeSourceManager()
    
    # Test category identification
    claim_text = "Currently researching CRM solutions for sales team"
    entities = {'products': ['CRM'], 'activities': ['researching']}
    category = manager.identify_category_from_claim(claim_text, entities)
    print(f"Identified category: {category}")
    
    # Test getting alternative companies
    alternatives = manager.get_alternative_companies(
        category='crm',
        exclude={'salesforce', 'hubspot'},
        count=3
    )
    print(f"\nAlternative CRM companies:")
    for alt in alternatives:
        print(f"  {alt.name} ({alt.tier.value}) - {alt.domain}")
        print(f"    {alt.description}")
    
    # Test niche sources
    niche_sources = manager.get_niche_sources(
        category='crm',
        search_terms=['simple', 'small business'],
        count=2
    )
    print(f"\nNiche CRM sources:")
    for source in niche_sources:
        print(f"  {source.name} - {source.description}")
    
    # Test major company detection
    print(f"\nIs Salesforce major: {manager.is_major_company('Salesforce')}")
    print(f"Is Pipedrive major: {manager.is_major_company('Pipedrive')}")
    
    # Test exclusion terms
    exclusion_terms = manager.get_exclusion_terms_for_diversity('crm')
    print(f"\nExclusion terms for CRM: {exclusion_terms[:5]}...")  # Show first 5
    
    # Test rotation
    all_crm = manager.get_alternative_companies('crm', count=10)
    print(f"\nRotation test:")
    for i in range(3):
        rotated = manager.rotate_source_selection(all_crm, 'crm', candidate_index=i)
        print(f"  Candidate {i}: {rotated[0].name}, {rotated[1].name}")


if __name__ == '__main__':
    test_alternative_source_manager()