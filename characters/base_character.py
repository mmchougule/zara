from typing import Dict, List
from dataclasses import dataclass
import yaml
import logging

logger = logging.getLogger(__name__)

@dataclass
class CharacterConfig:
    name: str
    bio: List[str]
    style: Dict[str, List[str]]
    traits: Dict[str, List[str]]
    voice_patterns: List[str]
    themes: List[str]
    content_types: Dict[str, Dict]
    engagement_style: Dict[str, List[str]]
    target_accounts: List[str]
    content_strategies: Dict[str, Dict]

class BaseCharacter:
    def __init__(self, config: CharacterConfig, config_path: str = None):
        if config_path:
            self.config = self._load_config(config_path)
        else:
            self.config = config
        # print(config)
        # print(self.config)
        self.initialize_character()

    def _load_config(self, config_path: str) -> CharacterConfig:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            return CharacterConfig(**config_data)

    def initialize_character(self):
        logger.info(f"Initializing character: {self.config.get('name')}")
        self.name = self.config.get('name')
        self.bio = self.config.get('bio')
        self.style = self.config.get('style')
        self.traits = self.config.get('traits')
        self.voice_patterns = self.config.get('voice_patterns')
        self.themes = self.config.get('themes')
        self.content_types = self.config.get('content_types')
        self.engagement_style = self.config.get('engagement_style')
        self.target_accounts = self.config.get('target_accounts')
        self.content_strategies = self.config.get('content_strategies')

    def get_content_strategy(self, content_type: str) -> Dict:
        return self.content_strategies.get(content_type, {})

    def get_voice_pattern(self) -> str:
        return self.voice_patterns[0]  # Can be randomized or context-based

    def get_style_guidelines(self) -> Dict:
        return self.style 