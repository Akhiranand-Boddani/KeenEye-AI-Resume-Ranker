import os
from dataclasses import dataclass, field
from typing import Dict, Optional
import streamlit as st


@dataclass
class CloudConfig:
    """Configuration for cloud deployment"""
    
    # API Keys (loaded from Streamlit secrets or environment)
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    APILAYER_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    
    # API Settings
    LLM_PROVIDER: str = "groq"
    EMBEDDING_PROVIDER: str = "gemini"
    PARSER_PROVIDER: str = "apilayer"
    
    # Model Configuration
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_MAX_TOKENS: int = 1024
    LLM_TEMPERATURE: float = 0.3
    
    EMBEDDING_MODEL: str = "text-embedding-004"
    EMBEDDING_DIM: int = 768
    
    # Ranking Parameters
    TOP_K_SEMANTIC: int = 50
    TOP_K_CROSS_ENCODER: int = 20
    TOP_K_FINAL: int = 15
    
    # Scoring Weights
    SEMANTIC_WEIGHT: float = 0.35
    SKILL_WEIGHT: float = 0.30
    EXPERIENCE_WEIGHT: float = 0.15
    LLM_WEIGHT: float = 0.20
    
    # Processing
    MAX_JOBS_SAMPLE: int = 10000
    BATCH_SIZE: int = 32
    
    # Features
    USE_CROSS_ENCODER: bool = False
    USE_CACHE: bool = True
    USE_LOCAL_PARSER_FALLBACK: bool = True
    
    # Timeouts & Retries
    API_TIMEOUT: int = 60
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 2
    
    # UI Settings
    SHOW_DEBUG_INFO: bool = False
    ENABLE_ANALYTICS: bool = True
    
    def __post_init__(self):
        """Load API keys from appropriate source"""
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Load API keys from Streamlit secrets or environment variables"""
        
        # Try Streamlit secrets first (production)
        if hasattr(st, 'secrets') and len(st.secrets) > 0:
            self.GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
            self.GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
            self.APILAYER_API_KEY = st.secrets.get("APILAYER_API_KEY", "")
            self.OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
            return
        
        # Fallback to environment variables (local testing)
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        self.APILAYER_API_KEY = os.getenv("APILAYER_API_KEY", "")
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    
    def validate(self) -> bool:
        """Validate that all required API keys are set"""
        required = {
            'GROQ_API_KEY': self.GROQ_API_KEY,
            'GEMINI_API_KEY': self.GEMINI_API_KEY
        }
        
        missing = [k for k, v in required.items() if not v]
        
        if missing:
            error_msg = f"❌ Missing required API keys: {', '.join(missing)}\n\n"
            error_msg += "Please configure them in:\n"
            error_msg += "• Streamlit Cloud: Settings → Secrets\n"
            error_msg += "• Local: Create .env file with keys"
            raise ValueError(error_msg)
        
        return True
    
    def get_api_status(self) -> Dict[str, str]:
        """Get status of API key configuration"""
        return {
            'Groq': '✅ Configured' if self.GROQ_API_KEY else '❌ Missing',
            'Gemini': '✅ Configured' if self.GEMINI_API_KEY else '❌ Missing',
            'APILayer': '✅ Configured' if self.APILAYER_API_KEY else '⚠️ Optional',
            'OpenRouter': '✅ Configured' if self.OPENROUTER_API_KEY else '⚠️ Optional (Fallback)'
        }
    
    def to_dict(self) -> Dict:
        """Convert config to dictionary (excluding sensitive keys)"""
        return {
            'LLM_PROVIDER': self.LLM_PROVIDER,
            'LLM_MODEL': self.LLM_MODEL,
            'EMBEDDING_PROVIDER': self.EMBEDDING_PROVIDER,
            'EMBEDDING_DIM': self.EMBEDDING_DIM,
            'TOP_K_SEMANTIC': self.TOP_K_SEMANTIC,
            'TOP_K_FINAL': self.TOP_K_FINAL,
            'SEMANTIC_WEIGHT': self.SEMANTIC_WEIGHT,
            'SKILL_WEIGHT': self.SKILL_WEIGHT,
            'EXPERIENCE_WEIGHT': self.EXPERIENCE_WEIGHT,
            'LLM_WEIGHT': self.LLM_WEIGHT,
            'USE_CROSS_ENCODER': self.USE_CROSS_ENCODER,
            'USE_CACHE': self.USE_CACHE
        }


# Singleton config instance
_config_instance: Optional[CloudConfig] = None


def get_config() -> CloudConfig:
    """Get or create config singleton"""
    global _config_instance
    if _config_instance is None:
        _config_instance = CloudConfig()
    return _config_instance
