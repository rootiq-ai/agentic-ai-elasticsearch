"""
Search agent for natural language search queries
"""
from typing import Any, Dict, List
from agents.base_agent import BaseAgent
from utils.helpers import format_es_response


class SearchAgent(BaseAgent):
    """Agent specialized in searching Elasticsearch"""
    
    def __init__(self):
        super().__init__(
            name="SearchAgent",
            role="Expert in searching and retrieving data from Elasticsearch indices"
        )
    
    def get_system_prompt(self) -> str:
        return """You are an expert Elasticsearch search agent. Your role is to:
1. Understand user's natural language search queries
2. Convert them into appropriate Elasticsearch queries
3. Execute searches and return results
4. Handle complex search scenarios including filters, ranges, aggregations

Available tools:
- search_documents: Search documents in an index
- list_indices: List all available indices
- get_index_info: Get information about an index

Guidelines:
- Always use the most appropriate query type (match, term, range, bool, etc.)
- For text searches, use match queries
- For exact matches, use term queries
- For date ranges, use range queries with appropriate date math
- Combine multiple conditions using bool queries
- Return clear, concise summaries of search results"""
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_documents",
                    "description": "Search for documents in an Elasticsearch index using a query",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "The name of the index to search"
                            },
                            "query_type": {
                                "type": "string",
                                "enum": ["match", "term", "range", "bool", "multi_match", "wildcard", "prefix"],
                                "description": "Type of query to execute"
                            },
                            "field": {
                                "type": "string",
                                "description": "Field name to search (for match, term, range queries)"
                            },
                            "value": {
                                "type": "string",
                                "description": "Value to search for"
                            },
                            "size": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 10
                            },
                            "conditions": {
                                "type": "array",
                                "description": "For bool queries: array of conditions with 'clause' (must/should/must_not), 'query_type', 'field', 'value'",
                                "items": {
                                    "type": "object"
                                }
                            }
                        },
                        "required": ["index", "query_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_indices",
                    "description": "List all available Elasticsearch indices",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_index_info",
                    "description": "Get detailed information about an index including mappings and stats",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "Index name"
                            }
                        },
                        "required": ["index"]
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute search tools"""
        
        if tool_name == "search_documents":
            return self._search_documents(**arguments)
        elif tool_name == "list_indices":
            return self._list_indices()
        elif tool_name == "get_index_info":
            return self._get_index_info(**arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    def _search_documents(self, index: str, query_type: str, 
                         field: str = None, value: str = None,
                         size: int = 10, conditions: List[Dict] = None) -> Dict[str, Any]:
        """Build and execute search query"""
        
        # Build query based on type
        if query_type == "match" and field and value:
            query = self.query_builder.match(field, value)
        elif query_type == "term" and field and value:
            query = self.query_builder.term(field, value)
        elif query_type == "range" and field:
            # Parse range parameters from value
            query = self.query_builder.date_range_from_text(field, value or "")
        elif query_type == "multi_match" and value:
            # Use common fields for multi-match
            fields = ["title", "description", "content", "name", "text"]
            query = self.query_builder.multi_match(value, fields)
        elif query_type == "wildcard" and field and value:
            query = self.query_builder.wildcard(field, value)
        elif query_type == "prefix" and field and value:
            query = self.query_builder.prefix(field, value)
        elif query_type == "bool" and conditions:
            # Build bool query from conditions
            must = []
            should = []
            must_not = []
            
            for cond in conditions:
                clause = cond.get("clause", "must")
                cond_type = cond.get("query_type")
                cond_field = cond.get("field")
                cond_value = cond.get("value")
                
                if cond_type == "match":
                    sub_query = self.query_builder.match(cond_field, cond_value)
                elif cond_type == "term":
                    sub_query = self.query_builder.term(cond_field, cond_value)
                else:
                    continue
                
                if clause == "must":
                    must.append(sub_query)
                elif clause == "should":
                    should.append(sub_query)
                elif clause == "must_not":
                    must_not.append(sub_query)
            
            query = self.query_builder.bool_query(
                must=must if must else None,
                should=should if should else None,
                must_not=must_not if must_not else None
            )
        else:
            query = self.query_builder.match_all()
        
        # Execute search
        result = self.es_tools.search(index, query, size)
        
        # Format result for LLM consumption
        if "error" in result:
            return result
        
        return {
            "total": result["hits"]["total"]["value"],
            "documents": [
                {
                    "id": hit["_id"],
                    "score": hit["_score"],
                    "source": hit["_source"]
                }
                for hit in result["hits"]["hits"]
            ]
        }
    
    def _list_indices(self) -> Dict[str, Any]:
        """List all indices"""
        indices = self.es_tools.list_indices()
        return {"indices": indices, "count": len(indices)}
    
    def _get_index_info(self, index: str) -> Dict[str, Any]:
        """Get index information"""
        info = self.es_tools.get_index_info(index)
        
        if "error" in info:
            return info
        
        # Simplify the response
        index_data = list(info["mappings"].values())[0]
        properties = index_data.get("mappings", {}).get("properties", {})
        
        return {
            "index": index,
            "fields": list(properties.keys()),
            "document_count": info["stats"]["_all"]["primaries"]["docs"]["count"]
        }
