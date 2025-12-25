"""
AI INSTRUCTION: Configuration Management
This file manages ALL application settings using Pydantic Settings.

RULES FOR AI:
1. ALL new config values go in the Settings class
2. Use environment variables for sensitive data
3. Provide sensible defaults for development
4. Document what each setting does
5. Never hardcode secrets in code

PATTERN: When you need a new config value:
  - Add it to Settings class with type hint
  - Provide default value if appropriate
  - Document its purpose
  - Access via: settings.YOUR_VALUE

AI: DO NOT create multiple config files. Everything goes here.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
     AI PATTERN: Application Settings
    
    This is the SINGLE source of truth for all configuration.
    
    How to add new settings:
    1. Add field with type annotation
    2. Provide default value or use Field()
    3. Add docstring explaining what it's for
    4. Environment variable name = UPPERCASE field name
    
    Example:
        new_feature_enabled: bool = Field(default=False, description="Enable new feature")
        # This reads from NEW_FEATURE_ENABLED env var
    """
    
    # APPLICATION SETTINGS

    app_name: str = Field(
        default="Backend Template",
        description="Application name - shown in API docs"
    )
    
    app_version: str = Field(
        default="0.1.0",
        description="Application version"
    )
    
    debug: bool = Field(
        default=True,
        description="Debug mode - DO NOT enable in production"
    )
    
    environment: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )
    
    # API SETTINGS   
    api_v1_prefix: str = Field(
        default="/api/v1",
        description="API v1 route prefix"
    )
    
    backend_cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins - restrict in production"
    )
    
    # DATABASE SETTINGS
    database_url: str = Field(
        default="sqlite:///./app.db",
        description="Database connection URL. Format: dialect://user:pass@host:port/db"
    )
    
    # AI: For PostgreSQL, user would set:
    # DATABASE_URL=postgresql://user:password@localhost:5432/dbname
    db_echo: bool = Field(
        default=False,
        description="Echo SQL queries - useful for debugging, disable in production"
    )
    
    # SECURITY SETTINGS
    secret_key: str = Field(
        default="CHANGE-THIS-IN-PRODUCTION-USE-RANDOM-STRING",
        description="Secret key for JWT tokens - MUST be changed in production"
    )
    
    algorithm: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    
    access_token_expire_minutes: int = Field(
        default=30,
        description="JWT token expiration time in minutes"
    )
    
    # LOGGING SETTINGS
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    
    # PYDANTIC SETTINGS CONFIGURATION
    model_config = SettingsConfigDict(
        env_file=".env",  # AI: Reads from .env file
        env_file_encoding="utf-8",
        case_sensitive=False,  # AI: Environment variables are case-insensitive
        extra="ignore"  # AI: Ignore extra environment variables
    )
    
    # VALIDATORS
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """AI PATTERN: Validate environment values"""
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v.lower()
    
    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """
        AI PATTERN: Handle CORS origins from environment variable
        
        Allows setting CORS origins as:
        - JSON list: ["http://localhost:3000"]
        - Comma-separated: "http://localhost:3000,http://localhost:8000"
        """
        if isinstance(v, str):
            # If it's a JSON string, try to parse it
            if v.startswith("["):
                import json
                return json.loads(v)
            # Otherwise split by comma
            return [origin.strip() for origin in v.split(",")]
        return v

# SETTINGS INSTANCE
@lru_cache
def get_settings() -> Settings:
    """
    AI PATTERN: Singleton Settings Instance
    
    This function ensures we only create ONE settings instance.
    Use this everywhere you need settings.
    
    Usage in your code:
        from app.core.config import settings
        
        # Access any setting:
        database_url = settings.database_url
        debug_mode = settings.debug
    
    AI: NEVER instantiate Settings() directly. Always use get_settings()
    """
    return Settings()


# AI: Export the settings instance for easy importing
settings = get_settings()


# AI USAGE EXAMPLES

"""
HOW AI SHOULD USE THIS FILE:

1. ACCESSING SETTINGS:
   ```python
   from app.core.config import settings
   
   if settings.debug:
       print("Debug  enabled")
   ```

2. ADDING NEW SETTINGS:
   Add to Settings class:
   ```python
   new_feature_timeout: int = Field(
       default=60,
       description="Timeout for new feature in seconds"
   )
   ```

3. ENVIRONMENT VARIABLES:
   Create .env file:
   ```
   DEBUG=False
   DATABASE_URL=postgresql://user:pass@localhost/db
   NEW_FEATURE_TIMEOUT=120
   ```

4. VALIDATION:
   Add validators when you need to validate/transform values:
   ```python
   @field_validator("new_feature_timeout")
   @classmethod
   def validate_timeout(cls, v: int) -> int:
       if v < 0:
           raise ValueError("Timeout must be positive")
       return v
   ```

AI: This file should RARELY be modified after initial setup.
Most changes will be adding new fields to Settings class.
"""