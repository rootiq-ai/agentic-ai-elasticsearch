"""
Query builder for Elasticsearch DSL
"""
from typing import Any, Dict, List, Optional
from utils.helpers import parse_date_range


class QueryBuilder:
    """Build Elasticsearch queries from natural language"""
    
    @staticmethod
    def match_all() -> Dict[str, Any]:
        """Build match_all query"""
        return {"match_all": {}}
    
    @staticmethod
    def match(field: str, value: str, operator: str = "or") -> Dict[str, Any]:
        """
        Build match query
        
        Args:
            field: Field name
            value: Search value
            operator: AND or OR
            
        Returns:
            Match query
        """
        return {
            "match": {
                field: {
                    "query": value,
                    "operator": operator
                }
            }
        }
    
    @staticmethod
    def term(field: str, value: Any) -> Dict[str, Any]:
        """
        Build term query for exact match
        
        Args:
            field: Field name
            value: Exact value
            
        Returns:
            Term query
        """
        return {"term": {field: value}}
    
    @staticmethod
    def terms(field: str, values: List[Any]) -> Dict[str, Any]:
        """
        Build terms query for multiple exact matches
        
        Args:
            field: Field name
            values: List of values
            
        Returns:
            Terms query
        """
        return {"terms": {field: values}}
    
    @staticmethod
    def range_query(field: str, gte=None, lte=None, gt=None, lt=None) -> Dict[str, Any]:
        """
        Build range query
        
        Args:
            field: Field name
            gte: Greater than or equal
            lte: Less than or equal
            gt: Greater than
            lt: Less than
            
        Returns:
            Range query
        """
        range_params = {}
        if gte is not None:
            range_params["gte"] = gte
        if lte is not None:
            range_params["lte"] = lte
        if gt is not None:
            range_params["gt"] = gt
        if lt is not None:
            range_params["lt"] = lt
        
        return {"range": {field: range_params}}
    
    @staticmethod
    def wildcard(field: str, pattern: str) -> Dict[str, Any]:
        """
        Build wildcard query
        
        Args:
            field: Field name
            pattern: Wildcard pattern
            
        Returns:
            Wildcard query
        """
        return {"wildcard": {field: pattern}}
    
    @staticmethod
    def prefix(field: str, value: str) -> Dict[str, Any]:
        """
        Build prefix query
        
        Args:
            field: Field name
            value: Prefix value
            
        Returns:
            Prefix query
        """
        return {"prefix": {field: value}}
    
    @staticmethod
    def exists(field: str) -> Dict[str, Any]:
        """
        Build exists query
        
        Args:
            field: Field name
            
        Returns:
            Exists query
        """
        return {"exists": {"field": field}}
    
    @staticmethod
    def bool_query(must: Optional[List[Dict]] = None,
                   should: Optional[List[Dict]] = None,
                   must_not: Optional[List[Dict]] = None,
                   filter: Optional[List[Dict]] = None,
                   minimum_should_match: int = 1) -> Dict[str, Any]:
        """
        Build bool query
        
        Args:
            must: Must conditions
            should: Should conditions
            must_not: Must not conditions
            filter: Filter conditions
            minimum_should_match: Minimum should match count
            
        Returns:
            Bool query
        """
        bool_params = {}
        
        if must:
            bool_params["must"] = must
        if should:
            bool_params["should"] = should
            bool_params["minimum_should_match"] = minimum_should_match
        if must_not:
            bool_params["must_not"] = must_not
        if filter:
            bool_params["filter"] = filter
        
        return {"bool": bool_params}
    
    @staticmethod
    def multi_match(query: str, fields: List[str], type: str = "best_fields") -> Dict[str, Any]:
        """
        Build multi_match query
        
        Args:
            query: Search query
            fields: List of fields to search
            type: Type of multi_match (best_fields, most_fields, cross_fields, phrase, phrase_prefix)
            
        Returns:
            Multi-match query
        """
        return {
            "multi_match": {
                "query": query,
                "fields": fields,
                "type": type
            }
        }
    
    @staticmethod
    def fuzzy(field: str, value: str, fuzziness: str = "AUTO") -> Dict[str, Any]:
        """
        Build fuzzy query
        
        Args:
            field: Field name
            value: Search value
            fuzziness: Fuzziness level (AUTO, 0, 1, 2)
            
        Returns:
            Fuzzy query
        """
        return {
            "fuzzy": {
                field: {
                    "value": value,
                    "fuzziness": fuzziness
                }
            }
        }
    
    @staticmethod
    def nested(path: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build nested query
        
        Args:
            path: Nested path
            query: Nested query
            
        Returns:
            Nested query
        """
        return {
            "nested": {
                "path": path,
                "query": query
            }
        }
    
    @staticmethod
    def date_range_from_text(field: str, text: str) -> Dict[str, Any]:
        """
        Build date range query from natural language
        
        Args:
            field: Date field name
            text: Natural language date description
            
        Returns:
            Range query
        """
        date_params = parse_date_range(text)
        return {"range": {field: date_params}}
    
    @staticmethod
    def aggregation_terms(field: str, size: int = 10) -> Dict[str, Any]:
        """
        Build terms aggregation
        
        Args:
            field: Field to aggregate
            size: Number of buckets
            
        Returns:
            Terms aggregation
        """
        return {
            "terms": {
                "field": field,
                "size": size
            }
        }
    
    @staticmethod
    def aggregation_date_histogram(field: str, interval: str = "1d") -> Dict[str, Any]:
        """
        Build date histogram aggregation
        
        Args:
            field: Date field
            interval: Interval (1d, 1w, 1M, etc.)
            
        Returns:
            Date histogram aggregation
        """
        return {
            "date_histogram": {
                "field": field,
                "interval": interval
            }
        }
    
    @staticmethod
    def aggregation_stats(field: str) -> Dict[str, Any]:
        """
        Build stats aggregation
        
        Args:
            field: Numeric field
            
        Returns:
            Stats aggregation
        """
        return {"stats": {"field": field}}
    
    @staticmethod
    def aggregation_avg(field: str) -> Dict[str, Any]:
        """
        Build average aggregation
        
        Args:
            field: Numeric field
            
        Returns:
            Average aggregation
        """
        return {"avg": {"field": field}}
    
    @staticmethod
    def aggregation_sum(field: str) -> Dict[str, Any]:
        """
        Build sum aggregation
        
        Args:
            field: Numeric field
            
        Returns:
            Sum aggregation
        """
        return {"sum": {"field": field}}
    
    @staticmethod
    def aggregation_cardinality(field: str) -> Dict[str, Any]:
        """
        Build cardinality (unique count) aggregation
        
        Args:
            field: Field name
            
        Returns:
            Cardinality aggregation
        """
        return {"cardinality": {"field": field}}
