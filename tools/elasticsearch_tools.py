"""
Elasticsearch tools for agent operations
"""
from typing import Any, Dict, List, Optional
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, RequestError
from config.config import config
from utils.logger import setup_logger

logger = setup_logger(__name__, "elasticsearch_tools.log")


class ElasticsearchTools:
    """Tools for interacting with Elasticsearch"""
    
    def __init__(self):
        """Initialize Elasticsearch client"""
        self.client = Elasticsearch(
            [config.elasticsearch.url],
            verify_certs=config.elasticsearch.verify_certs,
            request_timeout=config.timeout
        )
        
        # Test connection
        try:
            info = self.client.info()
            logger.info(f"Connected to Elasticsearch {info['version']['number']}")
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise
    
    def search(self, index: str, query: Dict[str, Any], size: int = 10) -> Dict[str, Any]:
        """
        Search documents in an index
        
        Args:
            index: Index name
            query: Query DSL
            size: Number of results
            
        Returns:
            Search results
        """
        try:
            logger.info(f"Searching index '{index}' with query: {query}")
            response = self.client.search(
                index=index,
                body={"query": query, "size": size}
            )
            logger.info(f"Found {response['hits']['total']['value']} documents")
            return response
        except NotFoundError:
            logger.error(f"Index '{index}' not found")
            return {"error": f"Index '{index}' not found"}
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"error": str(e)}
    
    def index_document(self, index: str, document: Dict[str, Any], doc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Index a document
        
        Args:
            index: Index name
            document: Document to index
            doc_id: Optional document ID
            
        Returns:
            Index response
        """
        try:
            logger.info(f"Indexing document to '{index}'")
            response = self.client.index(
                index=index,
                body=document,
                id=doc_id
            )
            logger.info(f"Document indexed with ID: {response['_id']}")
            return response
        except Exception as e:
            logger.error(f"Index error: {e}")
            return {"error": str(e)}
    
    def bulk_index(self, index: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk index documents
        
        Args:
            index: Index name
            documents: List of documents
            
        Returns:
            Bulk response
        """
        try:
            from elasticsearch.helpers import bulk
            
            actions = [
                {
                    "_index": index,
                    "_source": doc
                }
                for doc in documents
            ]
            
            logger.info(f"Bulk indexing {len(documents)} documents to '{index}'")
            success, failed = bulk(self.client, actions, raise_on_error=False)
            logger.info(f"Successfully indexed {success} documents, {failed} failed")
            
            return {
                "success": success,
                "failed": failed,
                "total": len(documents)
            }
        except Exception as e:
            logger.error(f"Bulk index error: {e}")
            return {"error": str(e)}
    
    def create_index(self, index: str, mappings: Optional[Dict[str, Any]] = None, 
                     settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create an index
        
        Args:
            index: Index name
            mappings: Index mappings
            settings: Index settings
            
        Returns:
            Create response
        """
        try:
            body = {}
            if mappings:
                body["mappings"] = mappings
            if settings:
                body["settings"] = settings
            
            logger.info(f"Creating index '{index}'")
            response = self.client.indices.create(index=index, body=body)
            logger.info(f"Index '{index}' created successfully")
            return response
        except RequestError as e:
            if "resource_already_exists_exception" in str(e):
                logger.warning(f"Index '{index}' already exists")
                return {"error": "Index already exists"}
            logger.error(f"Create index error: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Create index error: {e}")
            return {"error": str(e)}
    
    def delete_index(self, index: str) -> Dict[str, Any]:
        """
        Delete an index
        
        Args:
            index: Index name
            
        Returns:
            Delete response
        """
        try:
            logger.info(f"Deleting index '{index}'")
            response = self.client.indices.delete(index=index)
            logger.info(f"Index '{index}' deleted successfully")
            return response
        except NotFoundError:
            logger.error(f"Index '{index}' not found")
            return {"error": f"Index '{index}' not found"}
        except Exception as e:
            logger.error(f"Delete index error: {e}")
            return {"error": str(e)}
    
    def get_index_info(self, index: str) -> Dict[str, Any]:
        """
        Get index information
        
        Args:
            index: Index name
            
        Returns:
            Index information
        """
        try:
            logger.info(f"Getting info for index '{index}'")
            mappings = self.client.indices.get_mapping(index=index)
            settings = self.client.indices.get_settings(index=index)
            stats = self.client.indices.stats(index=index)
            
            return {
                "mappings": mappings,
                "settings": settings,
                "stats": stats
            }
        except NotFoundError:
            logger.error(f"Index '{index}' not found")
            return {"error": f"Index '{index}' not found"}
        except Exception as e:
            logger.error(f"Get index info error: {e}")
            return {"error": str(e)}
    
    def list_indices(self) -> List[str]:
        """
        List all indices
        
        Returns:
            List of index names
        """
        try:
            logger.info("Listing all indices")
            indices = self.client.cat.indices(format="json")
            index_names = [idx["index"] for idx in indices if not idx["index"].startswith(".")]
            logger.info(f"Found {len(index_names)} indices")
            return index_names
        except Exception as e:
            logger.error(f"List indices error: {e}")
            return []
    
    def aggregate(self, index: str, aggregations: Dict[str, Any], 
                  query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform aggregations
        
        Args:
            index: Index name
            aggregations: Aggregation DSL
            query: Optional query filter
            
        Returns:
            Aggregation results
        """
        try:
            body = {"aggs": aggregations, "size": 0}
            if query:
                body["query"] = query
            
            logger.info(f"Running aggregations on index '{index}'")
            response = self.client.search(index=index, body=body)
            logger.info("Aggregations completed successfully")
            return response
        except Exception as e:
            logger.error(f"Aggregation error: {e}")
            return {"error": str(e)}
    
    def update_document(self, index: str, doc_id: str, 
                        update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a document
        
        Args:
            index: Index name
            doc_id: Document ID
            update: Update script or doc
            
        Returns:
            Update response
        """
        try:
            logger.info(f"Updating document {doc_id} in index '{index}'")
            response = self.client.update(
                index=index,
                id=doc_id,
                body={"doc": update}
            )
            logger.info(f"Document {doc_id} updated successfully")
            return response
        except NotFoundError:
            logger.error(f"Document {doc_id} not found in index '{index}'")
            return {"error": "Document not found"}
        except Exception as e:
            logger.error(f"Update error: {e}")
            return {"error": str(e)}
    
    def delete_document(self, index: str, doc_id: str) -> Dict[str, Any]:
        """
        Delete a document
        
        Args:
            index: Index name
            doc_id: Document ID
            
        Returns:
            Delete response
        """
        try:
            logger.info(f"Deleting document {doc_id} from index '{index}'")
            response = self.client.delete(index=index, id=doc_id)
            logger.info(f"Document {doc_id} deleted successfully")
            return response
        except NotFoundError:
            logger.error(f"Document {doc_id} not found in index '{index}'")
            return {"error": "Document not found"}
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return {"error": str(e)}
