"""
Configuration management for Elasticsearch Agent
"""
import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class ElasticsearchConfig(BaseModel):
    """Elasticsearch configuration"""
    host: str = os.getenv("ELASTICSEARCH_HOST", "localhost")
    port: int = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
    user: Optional[str] = os.getenv("ELASTICSEARCH_USER")
    password: Optional[str] = os.getenv("ELASTICSEARCH_PASSWORD")
    scheme: str = os.getenv("ELASTICSEARCH_SCHEME", "http")
    verify_certs: bool = os.getenv("ELASTICSEARCH_VERIFY_CERTS", "False").lower() == "true"
    
    @property
    def url(self) -> str:
        """Get full Elasticsearch URL"""
        if self.user and self.password:
            return f"{self.scheme}://{self.user}:{self.password}@{self.host}:{self.port}"
        return f"{self.scheme}://{self.host}:{self.port}"


class OpenAIConfig(BaseModel):
    """OpenAI configuration"""
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))


class AppConfig(BaseModel):
    """Application configuration"""
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    timeout: int = int(os.getenv("TIMEOUT", "30"))
    
    elasticsearch: ElasticsearchConfig = ElasticsearchConfig()
    openai: OpenAIConfig = OpenAIConfig()


# Global config instance
config = AppConfig()
