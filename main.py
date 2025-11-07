"""
Main application entry point for Elasticsearch Agentic AI
"""
import sys
from agents.search_agent import SearchAgent
from agents.index_agent import IndexAgent
from agents.analytics_agent import AnalyticsAgent
from utils.logger import setup_logger

logger = setup_logger(__name__, "main.log")


class ElasticsearchAgentSystem:
    """Main system for orchestrating Elasticsearch agents"""
    
    def __init__(self):
        """Initialize all agents"""
        logger.info("Initializing Elasticsearch Agent System")
        
        self.search_agent = SearchAgent()
        self.index_agent = IndexAgent()
        self.analytics_agent = AnalyticsAgent()
        
        logger.info("All agents initialized successfully")
    
    def route_query(self, query: str) -> str:
        """
        Route query to appropriate agent based on intent
        
        Args:
            query: User query
            
        Returns:
            Agent response
        """
        query_lower = query.lower()
        
        # Index management keywords
        index_keywords = [
            "create index", "delete index", "index document", 
            "bulk index", "update document", "delete document",
            "add data", "insert", "remove", "modify"
        ]
        
        # Analytics keywords
        analytics_keywords = [
            "analyze", "statistics", "average", "sum", "count",
            "top", "histogram", "trend", "distribution",
            "how many", "what is the", "calculate", "aggregate"
        ]
        
        # Route to appropriate agent
        if any(keyword in query_lower for keyword in index_keywords):
            logger.info("Routing to IndexAgent")
            return self.index_agent.execute(query)
        elif any(keyword in query_lower for keyword in analytics_keywords):
            logger.info("Routing to AnalyticsAgent")
            return self.analytics_agent.execute(query)
        else:
            logger.info("Routing to SearchAgent")
            return self.search_agent.execute(query)
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("=" * 60)
        print("Elasticsearch Agentic AI System")
        print("=" * 60)
        print("\nAvailable commands:")
        print("  - Ask questions in natural language")
        print("  - Type 'exit' or 'quit' to exit")
        print("  - Type 'help' for examples")
        print()
        
        while True:
            try:
                query = input("You: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['exit', 'quit']:
                    print("\nGoodbye!")
                    break
                
                if query.lower() == 'help':
                    self._show_examples()
                    continue
                
                print("\nAgent: ", end="", flush=True)
                response = self.route_query(query)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"\nError: {e}\n")
    
    def _show_examples(self):
        """Show example queries"""
        print("\nExample queries:")
        print("\nSearch queries:")
        print("  - Find all users registered in the last week")
        print("  - Search for products with 'laptop' in the description")
        print("  - Show me documents where status is 'active'")
        
        print("\nIndex management:")
        print("  - Create an index called 'products'")
        print("  - Index a document with name='John' and age=30 in users index")
        print("  - Delete the 'old_data' index")
        
        print("\nAnalytics:")
        print("  - What are the top 10 most common product categories?")
        print("  - Calculate average price of all products")
        print("  - Show me the distribution of users by country")
        print()


def main():
    """Main function"""
    try:
        # Initialize system
        system = ElasticsearchAgentSystem()
        
        # Check if query provided as command line argument
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])
            logger.info(f"Processing query: {query}")
            response = system.route_query(query)
            print(response)
        else:
            # Run in interactive mode
            system.interactive_mode()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
