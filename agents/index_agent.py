"""
Index management agent
"""
from typing import Any, Dict, List
from agents.base_agent import BaseAgent
from utils.helpers import sanitize_index_name


class IndexAgent(BaseAgent):
    """Agent specialized in index management"""
    
    def __init__(self):
        super().__init__(
            name="IndexAgent",
            role="Expert in managing Elasticsearch indices and documents"
        )
    
    def get_system_prompt(self) -> str:
        return """You are an expert Elasticsearch index management agent. Your role is to:
1. Create and configure Elasticsearch indices
2. Index, update, and delete documents
3. Manage index settings and mappings
4. Perform bulk operations

Available tools:
- create_index: Create a new index with optional mappings and settings
- delete_index: Delete an index
- index_document: Index a single document
- bulk_index_documents: Index multiple documents at once
- update_document: Update an existing document
- delete_document: Delete a document
- list_indices: List all indices

Guidelines:
- Always sanitize index names (lowercase, no special chars)
- Suggest appropriate mappings based on data structure
- Use bulk operations for multiple documents
- Confirm destructive operations (delete)
- Provide clear feedback on operation success/failure"""
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_index",
                    "description": "Create a new Elasticsearch index",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "Index name (will be sanitized)"
                            },
                            "mappings": {
                                "type": "object",
                                "description": "Index mappings defining field types"
                            },
                            "settings": {
                                "type": "object",
                                "description": "Index settings (shards, replicas, etc.)"
                            }
                        },
                        "required": ["index"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_index",
                    "description": "Delete an Elasticsearch index",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "Index name to delete"
                            }
                        },
                        "required": ["index"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "index_document",
                    "description": "Index a single document",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "Index name"
                            },
                            "document": {
                                "type": "object",
                                "description": "Document to index"
                            },
                            "doc_id": {
                                "type": "string",
                                "description": "Optional document ID"
                            }
                        },
                        "required": ["index", "document"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "bulk_index_documents",
                    "description": "Index multiple documents at once",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "Index name"
                            },
                            "documents": {
                                "type": "array",
                                "description": "Array of documents to index",
                                "items": {
                                    "type": "object"
                                }
                            }
                        },
                        "required": ["index", "documents"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_document",
                    "description": "Update an existing document",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "Index name"
                            },
                            "doc_id": {
                                "type": "string",
                                "description": "Document ID"
                            },
                            "update": {
                                "type": "object",
                                "description": "Fields to update"
                            }
                        },
                        "required": ["index", "doc_id", "update"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_document",
                    "description": "Delete a document",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "Index name"
                            },
                            "doc_id": {
                                "type": "string",
                                "description": "Document ID to delete"
                            }
                        },
                        "required": ["index", "doc_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_indices",
                    "description": "List all available indices",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute index management tools"""
        
        if tool_name == "create_index":
            return self._create_index(**arguments)
        elif tool_name == "delete_index":
            return self._delete_index(**arguments)
        elif tool_name == "index_document":
            return self._index_document(**arguments)
        elif tool_name == "bulk_index_documents":
            return self._bulk_index_documents(**arguments)
        elif tool_name == "update_document":
            return self._update_document(**arguments)
        elif tool_name == "delete_document":
            return self._delete_document(**arguments)
        elif tool_name == "list_indices":
            return self._list_indices()
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    def _create_index(self, index: str, mappings: Dict = None, 
                     settings: Dict = None) -> Dict[str, Any]:
        """Create an index"""
        sanitized_name = sanitize_index_name(index)
        result = self.es_tools.create_index(sanitized_name, mappings, settings)
        
        if "error" in result:
            return result
        
        return {
            "success": True,
            "index": sanitized_name,
            "message": f"Index '{sanitized_name}' created successfully"
        }
    
    def _delete_index(self, index: str) -> Dict[str, Any]:
        """Delete an index"""
        result = self.es_tools.delete_index(index)
        
        if "error" in result:
            return result
        
        return {
            "success": True,
            "message": f"Index '{index}' deleted successfully"
        }
    
    def _index_document(self, index: str, document: Dict, 
                       doc_id: str = None) -> Dict[str, Any]:
        """Index a document"""
        result = self.es_tools.index_document(index, document, doc_id)
        
        if "error" in result:
            return result
        
        return {
            "success": True,
            "doc_id": result["_id"],
            "index": result["_index"],
            "message": f"Document indexed successfully with ID: {result['_id']}"
        }
    
    def _bulk_index_documents(self, index: str, 
                             documents: List[Dict]) -> Dict[str, Any]:
        """Bulk index documents"""
        result = self.es_tools.bulk_index(index, documents)
        
        if "error" in result:
            return result
        
        return {
            "success": True,
            "total": result["total"],
            "indexed": result["success"],
            "failed": result["failed"],
            "message": f"Indexed {result['success']} documents successfully"
        }
    
    def _update_document(self, index: str, doc_id: str, 
                        update: Dict) -> Dict[str, Any]:
        """Update a document"""
        result = self.es_tools.update_document(index, doc_id, update)
        
        if "error" in result:
            return result
        
        return {
            "success": True,
            "doc_id": doc_id,
            "message": f"Document {doc_id} updated successfully"
        }
    
    def _delete_document(self, index: str, doc_id: str) -> Dict[str, Any]:
        """Delete a document"""
        result = self.es_tools.delete_document(index, doc_id)
        
        if "error" in result:
            return result
        
        return {
            "success": True,
            "doc_id": doc_id,
            "message": f"Document {doc_id} deleted successfully"
        }
    
    def _list_indices(self) -> Dict[str, Any]:
        """List all indices"""
        indices = self.es_tools.list_indices()
        return {
            "indices": indices,
            "count": len(indices)
        }
