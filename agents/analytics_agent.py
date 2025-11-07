"""
Analytics agent for data aggregations and analysis
"""
from typing import Any, Dict, List
from agents.base_agent import BaseAgent
from utils.helpers import format_aggregation_response


class AnalyticsAgent(BaseAgent):
    """Agent specialized in data analytics and aggregations"""
    
    def __init__(self):
        super().__init__(
            name="AnalyticsAgent",
            role="Expert in analyzing data using Elasticsearch aggregations"
        )
    
    def get_system_prompt(self) -> str:
        return """You are an expert Elasticsearch analytics agent. Your role is to:
1. Perform data aggregations and analysis
2. Calculate statistics (avg, sum, min, max, count)
3. Create histograms and date-based analyses
4. Generate insights from data

Available tools:
- terms_aggregation: Group by field values and count occurrences
- date_histogram: Analyze data over time periods
- stats_aggregation: Calculate statistical metrics (avg, sum, min, max, count)
- cardinality_aggregation: Count unique values
- multi_aggregation: Combine multiple aggregations

Guidelines:
- Choose appropriate aggregation types based on the question
- Use date_histogram for time-based analysis
- Use terms for categorical grouping
- Use stats for numerical analysis
- Provide clear interpretations of results"""
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "terms_aggregation",
                    "description": "Group documents by field values and count occurrences (top N most common values)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "Index name"
                            },
                            "field": {
                                "type": "string",
                                "description": "Field to aggregate on (must be keyword type)"
                            },
                            "size": {
                                "type": "integer",
                                "description": "Number of top buckets to return",
                                "default": 10
                            },
                            "query": {
                                "type": "object",
                                "description": "Optional query to filter documents before aggregation"
                            }
                        },
                        "required": ["index", "field"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "date_histogram",
                    "description": "Analyze data over time periods (by day, week, month, etc.)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "Index name"
                            },
                            "field": {
                                "type": "string",
                                "description": "Date field to histogram on"
                            },
                            "interval": {
                                "type": "string",
                                "enum": ["1h", "1d", "1w", "1M", "1y"],
                                "description": "Time interval for buckets"
                            },
                            "query": {
                                "type": "object",
                                "description": "Optional query to filter documents"
                            }
                        },
                        "required": ["index", "field", "interval"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "stats_aggregation",
                    "description": "Calculate statistical metrics (count, sum, avg, min, max) for a numeric field",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "Index name"
                            },
                            "field": {
                                "type": "string",
                                "description": "Numeric field to analyze"
                            },
                            "query": {
                                "type": "object",
                                "description": "Optional query to filter documents"
                            }
                        },
                        "required": ["index", "field"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cardinality_aggregation",
                    "description": "Count unique values in a field",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "Index name"
                            },
                            "field": {
                                "type": "string",
                                "description": "Field to count unique values"
                            },
                            "query": {
                                "type": "object",
                                "description": "Optional query to filter documents"
                            }
                        },
                        "required": ["index", "field"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "multi_aggregation",
                    "description": "Perform multiple aggregations at once",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "Index name"
                            },
                            "aggregations": {
                                "type": "array",
                                "description": "Array of aggregation definitions",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "type": {"type": "string"},
                                        "field": {"type": "string"},
                                        "params": {"type": "object"}
                                    }
                                }
                            },
                            "query": {
                                "type": "object",
                                "description": "Optional query to filter documents"
                            }
                        },
                        "required": ["index", "aggregations"]
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute analytics tools"""
        
        if tool_name == "terms_aggregation":
            return self._terms_aggregation(**arguments)
        elif tool_name == "date_histogram":
            return self._date_histogram(**arguments)
        elif tool_name == "stats_aggregation":
            return self._stats_aggregation(**arguments)
        elif tool_name == "cardinality_aggregation":
            return self._cardinality_aggregation(**arguments)
        elif tool_name == "multi_aggregation":
            return self._multi_aggregation(**arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    def _terms_aggregation(self, index: str, field: str, 
                          size: int = 10, query: Dict = None) -> Dict[str, Any]:
        """Perform terms aggregation"""
        agg = {
            "top_terms": self.query_builder.aggregation_terms(field, size)
        }
        
        result = self.es_tools.aggregate(index, agg, query)
        
        if "error" in result:
            return result
        
        # Format results
        buckets = result["aggregations"]["top_terms"]["buckets"]
        
        return {
            "total_docs": result["hits"]["total"]["value"],
            "results": [
                {
                    "value": bucket["key"],
                    "count": bucket["doc_count"]
                }
                for bucket in buckets
            ]
        }
    
    def _date_histogram(self, index: str, field: str, 
                       interval: str, query: Dict = None) -> Dict[str, Any]:
        """Perform date histogram aggregation"""
        agg = {
            "timeline": self.query_builder.aggregation_date_histogram(field, interval)
        }
        
        result = self.es_tools.aggregate(index, agg, query)
        
        if "error" in result:
            return result
        
        # Format results
        buckets = result["aggregations"]["timeline"]["buckets"]
        
        return {
            "total_docs": result["hits"]["total"]["value"],
            "timeline": [
                {
                    "date": bucket["key_as_string"],
                    "count": bucket["doc_count"]
                }
                for bucket in buckets
            ]
        }
    
    def _stats_aggregation(self, index: str, field: str, 
                          query: Dict = None) -> Dict[str, Any]:
        """Perform stats aggregation"""
        agg = {
            "statistics": self.query_builder.aggregation_stats(field)
        }
        
        result = self.es_tools.aggregate(index, agg, query)
        
        if "error" in result:
            return result
        
        stats = result["aggregations"]["statistics"]
        
        return {
            "total_docs": result["hits"]["total"]["value"],
            "statistics": {
                "count": stats["count"],
                "sum": stats["sum"],
                "avg": stats["avg"],
                "min": stats["min"],
                "max": stats["max"]
            }
        }
    
    def _cardinality_aggregation(self, index: str, field: str, 
                                 query: Dict = None) -> Dict[str, Any]:
        """Count unique values"""
        agg = {
            "unique_count": self.query_builder.aggregation_cardinality(field)
        }
        
        result = self.es_tools.aggregate(index, agg, query)
        
        if "error" in result:
            return result
        
        return {
            "total_docs": result["hits"]["total"]["value"],
            "unique_count": result["aggregations"]["unique_count"]["value"]
        }
    
    def _multi_aggregation(self, index: str, aggregations: List[Dict], 
                          query: Dict = None) -> Dict[str, Any]:
        """Perform multiple aggregations"""
        agg_dict = {}
        
        for agg_def in aggregations:
            name = agg_def["name"]
            agg_type = agg_def["type"]
            field = agg_def["field"]
            params = agg_def.get("params", {})
            
            if agg_type == "terms":
                agg_dict[name] = self.query_builder.aggregation_terms(
                    field, params.get("size", 10)
                )
            elif agg_type == "stats":
                agg_dict[name] = self.query_builder.aggregation_stats(field)
            elif agg_type == "avg":
                agg_dict[name] = self.query_builder.aggregation_avg(field)
            elif agg_type == "sum":
                agg_dict[name] = self.query_builder.aggregation_sum(field)
            elif agg_type == "cardinality":
                agg_dict[name] = self.query_builder.aggregation_cardinality(field)
        
        result = self.es_tools.aggregate(index, agg_dict, query)
        
        if "error" in result:
            return result
        
        # Format all aggregation results
        formatted_results = {
            "total_docs": result["hits"]["total"]["value"],
            "aggregations": {}
        }
        
        for name, agg_result in result["aggregations"].items():
            if "buckets" in agg_result:
                formatted_results["aggregations"][name] = [
                    {"value": b["key"], "count": b["doc_count"]}
                    for b in agg_result["buckets"]
                ]
            elif "value" in agg_result:
                formatted_results["aggregations"][name] = agg_result["value"]
            else:
                formatted_results["aggregations"][name] = agg_result
        
        return formatted_results
