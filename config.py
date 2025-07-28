from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, Any
import os
import warnings
from ast import literal_eval


class Config(BaseSettings):
    """Application configuration using Pydantic BaseSettings.
    
    Environment variables can be prefixed with APP22_ (e.g., APP22_DEBUG=1).
    """
    
    model_config = SettingsConfigDict(
        env_prefix='APP22_',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    # Application Settings
    version: Optional[str] = Field(
        default=None,
        description="Application version"
    )
    
    secret_key: str = Field(
        default="app22-development-key-change-in-production",
        description="Secret key for session management"
    )
    
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    # Database Settings
    db_url: str = Field(
        default="sqlite:///app22.db",
        description="Database connection URI"
    )
    
    db_echo: bool = Field(
        default=False,
        description="Enable SQLAlchemy query logging"
    )
    
    db_options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional SQLAlchemy engine options"
    )
    
    # Server Settings
    host: str = Field(
        default="0.0.0.0",
        description="Server host address"
    )
    
    port: int = Field(
        default=5000,
        description="Server port"
    )
    
    # Computed properties for backward compatibility
    @property
    def VERSION(self) -> Optional[str]:
        return self.version
        
    @property
    def SECRET_KEY(self) -> str:
        return self.secret_key
        
    @property
    def DEBUG(self) -> bool:
        return self.debug
        
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.db_url
        
    @property
    def SQLALCHEMY_ECHO(self) -> bool:
        return self.db_echo
        
    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> Dict[str, Any]:
        return self.db_options
    
    # Modern property names
    @property
    def database_uri(self) -> str:
        return self.db_url
        
    @property
    def database_echo(self) -> bool:
        return self.db_echo
        
    @property
    def database_options(self) -> Dict[str, Any]:
        return self.db_options

    @field_validator('db_options', mode='before')
    @classmethod
    def parse_database_options(cls, v):
        """Parse database options from string if needed."""
        if isinstance(v, str):
            try:
                return literal_eval(v)
            except (ValueError, SyntaxError):
                return {}
        return v or {}
    
    @field_validator('debug', mode='before')
    @classmethod
    def parse_debug(cls, v):
        """Parse debug flag from various formats."""
        if isinstance(v, str):
            return v.lower() in ('1', 'true', 'yes', 'on')
        return bool(v)
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v):
        """Ensure secret key is secure in production."""
        if not v:
            raise ValueError("SECRET_KEY cannot be empty")
        
        # Warn about default key in production
        if v == "app22-development-key-change-in-production":
            warnings.warn(
                "Using default secret key! Change APP22_SECRET_KEY in production.",
                UserWarning
            )
        
        return v


# Global configuration instance
config = Config()

# Backward compatibility - expose as class for existing code
Config = config
