# Elasticsearch Agentic AI System

A production-ready agentic AI system for Elasticsearch operations using OpenAI's GPT models. This system allows users to interact with Elasticsearch using natural language queries, automatically routing requests to specialized agents.

## Features

- **Search Agent**: Natural language search queries with intelligent query building
- **Analytics Agent**: Data analysis and aggregations (statistics, histograms, trends)
- **Index Agent**: Index and document management operations
- **Intelligent Routing**: Automatically routes queries to the appropriate agent
- **Tool-Based Architecture**: Extensible and modular design
- **Comprehensive Logging**: Detailed operation tracking
- **Function Calling**: Uses OpenAI's function calling for precise tool execution

## Project Structure

```
elasticsearch-agent/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── config/
│   ├── __init__.py
│   └── config.py                 # Configuration management
├── agents/
│   ├── __init__.py
│   ├── base_agent.py            # Base agent class
│   ├── search_agent.py          # Search operations
│   ├── index_agent.py           # Index management
│   └── analytics_agent.py       # Analytics & aggregations
├── tools/
│   ├── __init__.py
│   ├── elasticsearch_tools.py   # ES client wrapper
│   └── query_builder.py         # Query DSL builder
├── utils/
│   ├── __init__.py
│   ├── logger.py                # Logging utilities
│   └── helpers.py               # Helper functions
└── main.py                      # Application entry point
```

## Installation

### Prerequisites

- Python 3.8+
- Elasticsearch 8.x
- OpenAI API key

### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd elasticsearch-agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Create empty __init__.py files**
```bash
touch config/__init__.py
touch agents/__init__.py
touch tools/__init__.py
touch utils/__init__.py
```

## Configuration

Edit `.env` file with your settings:

```env
# OpenAI
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=changeme
ELASTICSEARCH_SCHEME=http

# Application
LOG_LEVEL=INFO
```

## Usage

### Interactive Mode

Run the application in interactive mode:

```bash
python main.py
```

### Command Line Mode

Execute a single query:

```bash
python main.py "Find all users registered in the last week"
```

### Example Queries

#### Search Operations
```python
# Natural language search
"Find all products with 'laptop' in the description"
"Show me active users from last month"
"Search for documents where status is pending"

# Complex searches
"Find products priced between 100 and 500"
"Show users who registered yesterday"
```

#### Index Management
```python
# Create indices
"Create an index called 'products'"
"Create a users index with email and name fields"

# Index documents
"Add a document to products: name='Laptop', price=999"
"Index multiple products from this data: [...]"

# Modify indices
"Update document abc123 in users index, set status='active'"
"Delete the old_data index"
```

#### Analytics
```python
# Aggregations
"What are the top 10 product categories?"
"Show me the distribution of users by country"

# Statistics
"Calculate the average price of all products"
"What's the total revenue in the last month?"

# Time-based analysis
"Show daily user registrations for the past week"
"Analyze sales trends by month"
```

### Programmatic Usage

```python
from agents.search_agent import SearchAgent
from agents.index_agent import IndexAgent
from agents.analytics_agent import AnalyticsAgent

# Initialize agents
search_agent = SearchAgent()
index_agent = IndexAgent()
analytics_agent = AnalyticsAgent()

# Execute queries
search_result = search_agent.execute("Find all active users")
index_result = index_agent.execute("Create an index called test_index")
analytics_result = analytics_agent.execute("What are the top 10 countries?")

print(search_result)
```

## Architecture

### Agent System

The system uses three specialized agents:

1. **SearchAgent**: Handles search queries
   - Full-text search
   - Filtered queries
   - Complex boolean queries
   - Multi-field searches

2. **IndexAgent**: Manages indices and documents
   - Create/delete indices
   - Index documents (single and bulk)
   - Update/delete documents
   - Index configuration

3. **AnalyticsAgent**: Performs data analysis
   - Terms aggregations
   - Date histograms
   - Statistical calculations
   - Multi-aggregations

### Tool Architecture

Each agent has access to specific tools through OpenAI's function calling:

```python
# Example tool definition
{
    "type": "function",
    "function": {
        "name": "search_documents",
        "description": "Search for documents in an index",
        "parameters": {
            "type": "object",
            "properties": {
                "index": {"type": "string"},
                "query_type": {"type": "string"},
                "field": {"type": "string"},
                "value": {"type": "string"}
            }
        }
    }
}
```

### Query Flow

1. User submits natural language query
2. System routes query to appropriate agent
3. Agent uses OpenAI to understand intent
4. Agent selects and executes appropriate tools
5. Results are formatted and returned to user

## Advanced Usage

### Custom Query Building

```python
from tools.query_builder import QueryBuilder

qb = QueryBuilder()

# Build complex queries
query = qb.bool_query(
    must=[
        qb.match("title", "laptop"),
        qb.range_query("price", gte=500, lte=1500)
    ],
    should=[
        qb.term("brand.keyword", "Dell"),
        qb.term("brand.keyword", "HP")
    ]
)
```

### Direct Elasticsearch Operations

```python
from tools.elasticsearch_tools import ElasticsearchTools

es = ElasticsearchTools()

# Direct search
result = es.search("products", {"match_all": {}}, size=10)

# Create index with mappings
mappings = {
    "properties": {
        "title": {"type": "text"},
        "price": {"type": "float"},
        "created_at": {"type": "date"}
    }
}
es.create_index("products", mappings)
```

## Logging

Logs are stored in the `logs/` directory:

- `main.log`: Application-level logs
- `base_agent.log`: Agent operations
- `elasticsearch_tools.log`: Elasticsearch operations

Log level can be configured in `.env`:
```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## Testing

Run tests (to be implemented):

```bash
pytest tests/
```

## Troubleshooting

### Connection Issues

```bash
# Test Elasticsearch connection
curl http://localhost:9200

# Check Elasticsearch status
curl http://localhost:9200/_cluster/health
```

### API Key Issues

Ensure your OpenAI API key is valid:
```bash
echo $OPENAI_API_KEY
```

### Import Errors

Make sure all `__init__.py` files exist:
```bash
find . -type d -name "__pycache__" -prune -o -type d -print | grep -E "(config|agents|tools|utils)" | xargs -I {} touch {}/__init__.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - feel free to use this project for any purpose.

## Acknowledgments

- Built with [OpenAI GPT-4](https://openai.com)
- Uses [Elasticsearch Python Client](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html)
- Inspired by agentic AI patterns

## Support

For issues and questions:
- Open an issue on GitHub
- Check Elasticsearch documentation
- Review OpenAI function calling docs

## Roadmap

- [ ] Add more agent types (optimization, monitoring)
- [ ] Implement caching layer
- [ ] Add async support
- [ ] Create web UI
- [ ] Add more aggregation types
- [ ] Implement query suggestions
- [ ] Add authentication/authorization
- [ ] Create Docker setup
- [ ] Add comprehensive tests
- [ ] Implement streaming responses

---

Made with ❤️ for the Elasticsearch and AI community
