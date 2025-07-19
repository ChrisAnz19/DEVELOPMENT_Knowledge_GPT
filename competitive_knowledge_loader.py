"""
Simple competitive knowledge base loader for smart prompt interpretation.
"""
import json
import os
from typing import Dict, List, Optional


def load_competitive_knowledge() -> Dict:
    """
    Load competitive knowledge from JSON file.
    
    Returns:
        Dict containing competitive knowledge data
        
    Raises:
        FileNotFoundError: If competitive_knowledge.json is not found
        json.JSONDecodeError: If JSON is invalid
    """
    file_path = os.path.join(os.path.dirname(__file__), "competitive_knowledge.json")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_company_competitors(company_name: str, knowledge_data: Optional[Dict] = None) -> List[str]:
    """
    Get list of competitors for a given company.
    
    Args:
        company_name: Name of the company to find competitors for
        knowledge_data: Optional pre-loaded knowledge data
        
    Returns:
        List of competitor company names
    """
    if knowledge_data is None:
        try:
            knowledge_data = load_competitive_knowledge()
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    if not isinstance(knowledge_data, dict):
        return []
    
    companies = knowledge_data.get("companies", {})
    company_key = company_name.lower().strip()
    
    # Direct lookup
    if company_key in companies:
        return companies[company_key].get("competitors", [])
    
    # Check aliases
    for comp_key, comp_data in companies.items():
        aliases = comp_data.get("aliases", [])
        if company_key in [alias.lower() for alias in aliases]:
            return comp_data.get("competitors", [])
    
    return []


def get_category_info(category: str, knowledge_data: Optional[Dict] = None) -> Dict:
    """
    Get category information including buying indicators and exclusion patterns.
    
    Args:
        category: Category name to look up
        knowledge_data: Optional pre-loaded knowledge data
        
    Returns:
        Dict containing category information
    """
    if knowledge_data is None:
        try:
            knowledge_data = load_competitive_knowledge()
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    if not isinstance(knowledge_data, dict):
        return {}
    
    categories = knowledge_data.get("categories", {})
    return categories.get(category.lower(), {})


def find_company_category(company_name: str, knowledge_data: Optional[Dict] = None) -> Optional[str]:
    """
    Find the category for a given company.
    
    Args:
        company_name: Name of the company
        knowledge_data: Optional pre-loaded knowledge data
        
    Returns:
        Category name if found, None otherwise
    """
    if knowledge_data is None:
        try:
            knowledge_data = load_competitive_knowledge()
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    if not isinstance(knowledge_data, dict):
        return None
    
    companies = knowledge_data.get("companies", {})
    company_key = company_name.lower().strip()
    
    # Direct lookup
    if company_key in companies:
        return companies[company_key].get("category")
    
    # Check aliases
    for comp_key, comp_data in companies.items():
        aliases = comp_data.get("aliases", [])
        if company_key in [alias.lower() for alias in aliases]:
            return comp_data.get("category")
    
    return None