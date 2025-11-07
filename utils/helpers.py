"""
Helper utilities for the application
"""
import json
from typing import Any, Dict, List
from datetime import datetime


def format_es_response(response: Dict[str, Any]) -> str:
    """
    Format Elasticsearch response for display
    
    Args:
        response: Raw Elasticsearch response
        
    Returns:
        Formatted string representation
    """
    if "hits" in response:
        hits = response["hits"]["hits"]
        total = response["hits"]["total"]["value"]
        
        formatted = f"Found {total} documents:\n\n"
        for i, hit in enumerate(hits, 1):
            formatted += f"{i}. [ID: {hit['_id']}]\n"
            formatted += json.dumps(hit["_source"], indent=2)
            formatted += "\n\n"
        return formatted
    
    return json.dumps(response, indent=2)


def format_aggregation_response(response: Dict[str, Any]) -> str:
    """
    Format aggregation response for display
    
    Args:
        response: Aggregation response
        
    Returns:
        Formatted string
    """
    if "aggregations" not in response:
        return "No aggregations found"
    
    aggs = response["aggregations"]
    formatted = "Aggregation Results:\n\n"
    
    for key, value in aggs.items():
        formatted += f"{key}:\n"
        if "buckets" in value:
            for bucket in value["buckets"]:
                formatted += f"  - {bucket.get('key', 'N/A')}: {bucket.get('doc_count', 0)}\n"
        elif "value" in value:
            formatted += f"  Value: {value['value']}\n"
        formatted += "\n"
    
    return formatted


def parse_date_range(text: str) -> Dict[str, str]:
    """
    Parse natural language date ranges
    
    Args:
        text: Natural language date description
        
    Returns:
        Dictionary with 'gte' and/or 'lte' keys
    """
    text_lower = text.lower()
    result = {}
    
    if "last week" in text_lower or "past week" in text_lower:
        result["gte"] = "now-1w/d"
    elif "last month" in text_lower or "past month" in text_lower:
        result["gte"] = "now-1M/d"
    elif "last year" in text_lower or "past year" in text_lower:
        result["gte"] = "now-1y/d"
    elif "today" in text_lower:
        result["gte"] = "now/d"
    elif "yesterday" in text_lower:
        result["gte"] = "now-1d/d"
        result["lte"] = "now-1d/d"
    
    return result


def extract_field_names(query: str) -> List[str]:
    """
    Extract potential field names from query text
    
    Args:
        query: User query text
        
    Returns:
        List of potential field names
    """
    # Common field patterns
    field_indicators = [
        "field:", "column:", "attribute:", "property:",
        "in the", "from the", "by", "where"
    ]
    
    fields = []
    words = query.split()
    
    for i, word in enumerate(words):
        if word.lower() in field_indicators and i + 1 < len(words):
            potential_field = words[i + 1].strip(".,?!")
            fields.append(potential_field)
    
    return fields


def sanitize_index_name(name: str) -> str:
    """
    Sanitize index name according to Elasticsearch rules
    
    Args:
        name: Proposed index name
        
    Returns:
        Sanitized index name
    """
    # Convert to lowercase
    name = name.lower()
    
    # Replace spaces and invalid chars with underscores
    invalid_chars = [' ', '/', '\\', '*', '?', '"', '<', '>', '|', '#', ',']
    for char in invalid_chars:
        name = name.replace(char, '_')
    
    # Cannot start with -, _, +
    name = name.lstrip('-_+')
    
    # Cannot be . or ..
    if name in ['.', '..']:
        name = 'index_' + name
    
    return name


def build_must_query(conditions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a bool query with must conditions
    
    Args:
        conditions: List of query conditions
        
    Returns:
        Bool query dictionary
    """
    return {
        "bool": {
            "must": conditions
        }
    }


def build_should_query(conditions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a bool query with should conditions
    
    Args:
        conditions: List of query conditions
        
    Returns:
        Bool query dictionary
    """
    return {
        "bool": {
            "should": conditions,
            "minimum_should_match": 1
        }
    }
