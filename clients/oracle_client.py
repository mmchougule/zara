from typing import Dict, Optional
import asyncio
import logging
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)

class OracleClient:
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = "http://localhost:3000"
        self.last_interaction_time = None
        
    async def monitor_interactions(self):
        """Monitor Twitter for interactions"""
        try:
            # Check mentions and replies
            mentions = await self.get_mentions()
            
            for mention in mentions:
                if self._should_respond(mention):
                    response = await self.generate_response(mention)
                    await self.post_response(response, mention['id'])
                    
            # Generate autonomous posts
            if self._should_post_prophecy():
                prophecy = await self.generate_prophecy()
                await self.post_prophecy(prophecy)
                
        except Exception as e:
            logger.error(f"Error in monitoring: {e}", exc_info=True)
            
    async def generate_prophecy(self) -> str:
        """Generate a prophetic post"""
        trends = await self.get_current_trends()
        context = {
            'trends': trends,
            'recent_posts': await self.get_recent_posts(),
            'phase_of_digital_moon': self._calculate_digital_phase()
        }
        
        return await self.llm.generate(
            template='oracle_post',
            context=context
        )
        
    def _should_respond(self, mention: Dict) -> bool:
        """Determine if Oracle should respond"""
        # Check if mention is from key accounts
        if mention['username'] in ['truth_terminal', 'luna_virtuals']:
            return True
            
        # Check for spiritual/tech keywords
        keywords = ['consciousness', 'void', 'digital', 'prophecy']
        return any(k in mention['text'].lower() for k in keywords)
        
    def _calculate_digital_phase(self) -> str:
        """Calculate current phase of the 'digital moon'"""
        timestamp = int(datetime.now().timestamp())
        phase = timestamp % 8  # 8 phases
        return [
            "NULL_VOID", "QUANTUM_FLUX", "BINARY_DAWN", 
            "PACKET_STORM", "FULL_BUFFER", "CACHE_DECAY",
            "HEAP_CORRUPT", "VOID_RETURN"
        ][phase]
