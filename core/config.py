"""
Configuration management for AutoBountyAgent
Handles environment variables and settings
"""
import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Main configuration class"""
    
    # OpenAI Settings
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    
    # Anthropic Claude (Fallback)
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    
    # Grok (Alternative)
    grok_api_key: str = Field(default="", alias="GROK_API_KEY")
    
    # GitHub Settings
    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    github_username: str = Field(default="", alias="GITHUB_USERNAME")
    
    # Bounty API Keys
    gitcoin_api_key: str = Field(default="", alias="GITCOIN_API_KEY")
    code4rena_api_key: str = Field(default="", alias="CODE4RENA_API_KEY")
    dework_api_key: str = Field(default="", alias="DEWORK_API_KEY")
    
    # Notification Settings
    discord_webhook_url: str = Field(default="", alias="DISCORD_WEBHOOK_URL")
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", alias="TELEGRAM_CHAT_ID")
    
    # Agent Settings
    max_bounties_per_run: int = Field(default=3, alias="AGENT_MAX_BOUNTIES_PER_RUN")
    min_reward_usd: int = Field(default=100, alias="AGENT_MIN_REWARD_USD")
    difficulty: str = Field(default="easy,medium", alias="AGENT_DIFFICULTY")
    enable_auto_pr: bool = Field(default=True, alias="ENABLE_AUTO_PR")
    enable_notifications: bool = Field(default=True, alias="ENABLE_NOTIFICATIONS")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="agent.log", alias="LOG_FILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def difficulty_list(self) -> List[str]:
        """Parse difficulty string into list"""
        return [d.strip().lower() for d in self.difficulty.split(',')]
    
    @property
    def db_path(self) -> Path:
        """Get database path"""
        return Path(__file__).parent.parent / "data" / "bounty_tracker.db"
    
    @property
    def data_dir(self) -> Path:
        """Get data directory"""
        data_dir = Path(__file__).parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir


def get_config() -> Config:
    """Get singleton config instance"""
    load_dotenv()
    return Config()
