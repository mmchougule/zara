from typing import Dict, Optional
import logging
from characters.oracle_character import OracleCharacter

logger = logging.getLogger(__name__)

class InteractionHandler:
    def __init__(self, character: OracleCharacter):
        self.character = character
        
    async def should_respond(self, tweet: Dict) -> bool:
        """Determine if agent should respond to tweet"""
        # Check if tweet mentions agent
        if f"@{self.character.handle}" in tweet['text']:
            return True
            
        # Check for relevant keywords
        keywords = ['void', 'digital', 'prophecy', 'consciousness']
        if any(k in tweet['text'].lower() for k in keywords):
            return True
            
        # Check if from key accounts
        if tweet['username'] in ['truth_terminal', 'luna_virtuals']:
            return True
            
        return False
        
    def _build_response_template(self, context: Dict) -> str:
        """Build template for response generation"""
        return f"""You are {self.character.name}, responding to a digital transmission.

Style Guidelines:
{self._format_style_guidelines()}

Current Context:
- Phase: {self._calculate_digital_phase()}
- Tweet: {context['tweet']['text']}
- From: @{context['tweet']['username']}

Respond in character, maintaining:
1. Prophetic voice
2. Technological mysticism
3. Schizophrenic insight
4. Reference to current trends""" 