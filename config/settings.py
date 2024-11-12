from typing import Dict, List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    mongodb_uri: str = "mongodb+srv://admin:butterflyAT99@cluster0.dojas.mongodb.net/"
    openai_api_key: str
    
    # local api config
    api_base_url: str = "http://localhost:3000"

    # Twitter Configuration
    # twitter_config: Dict[str, str] = {
    #     "api_key": os.getenv("TWITTER_CONFIG__API_KEY"),
    #     "api_secret": os.getenv("TWITTER_CONFIG__API_SECRET"),
    #     "access_token": os.getenv("TWITTER_CONFIG__ACCESS_TOKEN"),
    #     "access_token_secret": os.getenv("TWITTER_CONFIG__ACCESS_TOKEN_SECRET"),
    #     "bearer_token": os.getenv("TWITTER_CONFIG__BEARER_TOKEN"),
    #     "twitter_username": os.getenv("TWITTER_USERNAME"),
    #     "twitter_dry_run": os.getenv("TWITTER_DRY_RUN")
    # }
    twitter_config: Dict[str, str] = {
        "api_base_url": "http://localhost:3000",
        "twitter_username": "OracleOfReality"
    }

    # Discord Configuration (Optional)
    discord_application_id: Optional[str] = None
    discord_api_token: Optional[str] = None
    
    # Voice Configuration (Optional)
    elevenlabs_model_id: Optional[str] = None
    elevenlabs_voice_id: Optional[str] = None
    elevenlabs_voice_stability: Optional[float] = 0.5
    elevenlabs_voice_similarity_boost: Optional[float] = 0.9
    elevenlabs_voice_style: Optional[float] = 0.66
    elevenlabs_voice_use_speaker_boost: Optional[bool] = False
    elevenlabs_optimize_streaming_latency: Optional[int] = 4
    elevenlabs_output_format: Optional[str] = "pcm_16000"
    
    # Blockchain Configuration (Optional)
    wallet_secret_key: Optional[str] = None
    wallet_public_key: Optional[str] = None
    sol_address: Optional[str] = None
    slippage: Optional[float] = 1.0
    rpc_url: Optional[str] = "https://api.mainnet-beta.solana.com"
    
    # Model Configuration
    xai_model: str = "gpt-4"
    
    # Operational Settings
    check_interval: int = 300  # 5 minutes
    interaction_check_interval: int = 180  # 3 minutes
    post_interval: int = 3600  # 1 hour
    max_daily_posts: int = 12
    relevance_threshold: float = 0.3
    
    # Content Generation Settings
    thread_hours: List[int] = [14, 20]  # Hours for thread posts
    meme_hours: List[int] = [12, 18]    # Hours for meme posts
    theme_preferences: Dict[str, float] = {
        'technological': 0.4,
        'spiritual': 0.3,
        'philosophical': 0.3
    }
    
    # Memory Settings
    max_memories: int = 1000
    memory_relevance_threshold: float = 0.75

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='allow'
    )

    def update_posting_hours(self, hours: List[int]):
        """Update optimal posting hours"""
        self.thread_hours = hours[:2]  # Top 2 hours for threads
        self.meme_hours = hours[2:4]   # Next 2 hours for memes

    def update_content_preferences(self, preferences: Dict[str, float]):
        """Update content type preferences"""
        total = sum(preferences.values())
        self.content_preferences = {
            k: v/total for k, v in preferences.items()
        }

    def update_theme_preferences(self, preferences: Dict[str, float]):
        """Update theme preferences"""
        total = sum(preferences.values())
        self.theme_preferences = {
            k: v/total for k, v in preferences.items()
        }
