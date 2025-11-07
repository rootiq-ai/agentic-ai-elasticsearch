"""
Base agent class for all Elasticsearch agents
"""
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from openai import OpenAI
from config.config import config
from tools.elasticsearch_tools import ElasticsearchTools
from tools.query_builder import QueryBuilder
from utils.logger import setup_logger

logger = setup_logger(__name__, "base_agent.log")


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, role: str):
        """
        Initialize base agent
        
        Args:
            name: Agent name
            role: Agent role description
        """
        self.name = name
        self.role = role
        self.client = OpenAI(api_key=config.openai.api_key)
        self.es_tools = ElasticsearchTools()
        self.query_builder = QueryBuilder()
        
        logger.info(f"Initialized {self.name} agent with role: {self.role}")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent
        
        Returns:
            System prompt string
        """
        pass
    
    @abstractmethod
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """
        Get the tools schema for function calling
        
        Returns:
            List of tool definitions
        """
        pass
    
    @abstractmethod
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a tool with given arguments
        
        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        pass
    
    def execute(self, user_query: str, max_iterations: int = 5) -> str:
        """
        Execute agent with user query
        
        Args:
            user_query: User's natural language query
            max_iterations: Maximum tool calling iterations
            
        Returns:
            Final response
        """
        logger.info(f"{self.name} executing query: {user_query}")
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_query}
        ]
        
        for iteration in range(max_iterations):
            logger.info(f"Iteration {iteration + 1}/{max_iterations}")
            
            try:
                response = self.client.chat.completions.create(
                    model=config.openai.model,
                    messages=messages,
                    tools=self.get_tools_schema(),
                    tool_choice="auto",
                    temperature=config.openai.temperature
                )
                
                response_message = response.choices[0].message
                messages.append(response_message)
                
                # Check if tool calls are needed
                if not response_message.tool_calls:
                    # No more tool calls, return final answer
                    final_response = response_message.content
                    logger.info(f"{self.name} completed successfully")
                    return final_response
                
                # Execute tool calls
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    
                    # Execute the tool
                    tool_result = self.execute_tool(tool_name, tool_args)
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(tool_result)
                    })
                    
                    logger.info(f"Tool {tool_name} executed successfully")
            
            except Exception as e:
                error_msg = f"Error in {self.name}: {str(e)}"
                logger.error(error_msg)
                return f"I encountered an error: {str(e)}"
        
        logger.warning(f"{self.name} reached maximum iterations")
        return "I've reached the maximum number of steps. The task may be too complex or require clarification."
    
    def format_response(self, data: Any) -> str:
        """
        Format data for display
        
        Args:
            data: Data to format
            
        Returns:
            Formatted string
        """
        if isinstance(data, dict):
            if "error" in data:
                return f"Error: {data['error']}"
            return json.dumps(data, indent=2)
        elif isinstance(data, list):
            return json.dumps(data, indent=2)
        else:
            return str(data)
