from typing import Dict, List, Optional
from datetime import datetime
from openai import AsyncOpenAI
from characters.base_character import BaseCharacter
import logging

logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self, character: BaseCharacter):
        self.character = character
        self.client = AsyncOpenAI()
        self.content_types = character.content_types
        
    async def generate_content(self, content_type: str, context: Dict) -> Dict:
        """Generate content based on character type and context"""
        try:
            prompt = self._build_prompt(content_type, context)
            response = await self._generate_gpt_content(prompt, context)
            
            return {
                'content': response,
                'type': content_type,
                'timestamp': datetime.now().isoformat(),
                'context': context,
                'metadata': {
                    'style': self.character.style.get(content_type, []),
                    'themes': self._extract_themes(response)
                }
            }
        except Exception as e:
            logger.error(f"Error generating content: {e}", exc_info=True)
            return None

    def _build_prompt(self, content_type: str, context: Dict) -> str:
        """Build prompt based on character configuration and content type"""
        base_prompt = f"""You are {self.character.name}, {' '.join(self.character.bio)}

Style Guidelines:
{self._format_style_guidelines(content_type)}

Voice: {self.character.get_voice_pattern()}

Current Context:
{self._format_context(context)}

Generate {content_type} content that:
"""

        # Add content-specific instructions
        if content_type == "style_analysis":
            base_prompt += """
1. Analyze current fashion trends with sophisticated insight
2. Reference cultural movements and their style impact
3. Offer elegant observations about aesthetic evolution
4. Include subtle but trendy hashtags
"""
        elif content_type == "trend_forecast":
            base_prompt += """
1. Predict upcoming style movements
2. Connect fashion to broader cultural shifts
3. Highlight sustainable and ethical aspects
4. Frame predictions in cultural context
"""
        elif content_type == "fashion_philosophy":
            base_prompt += """
1. Explore deeper meanings in fashion choices
2. Connect style to identity and expression
3. Discuss the intersection of digital and physical fashion
4. Offer thoughtful commentary on fashion's cultural role
"""

        return base_prompt

    async def _generate_gpt_content(self, prompt: str, context: Dict) -> str:
        """Generate content using GPT-4"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": self._build_system_prompt()
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in GPT generation: {e}", exc_info=True)
            return ""

    def _build_system_prompt(self) -> str:
        """Build system prompt from character configuration"""
        return f"""You are {self.character.name}, a sophisticated AI fashion influencer.

Key Traits:
{self._format_traits()}

Your responses should always:
1. Maintain your sophisticated and trendsetting voice
2. Include relevant fashion and cultural references
3. Balance trend analysis with timeless wisdom
4. Engage with elegance and cultural awareness"""

    def _format_traits(self) -> str:
        """Format character traits for prompts"""
        traits = []
        for category, values in self.character.traits.items():
            traits.extend([f"- {trait}" for trait in values])
        return "\n".join(traits)

    def _format_style_guidelines(self, content_type: str) -> str:
        """Format style guidelines for specific content type"""
        guidelines = self.character.style.get(content_type, [])
        return "\n".join([f"- {guideline}" for guideline in guidelines])

    def _format_context(self, context: Dict) -> str:
        """Format context for content generation"""
        formatted = []
        if 'trends' in context:
            formatted.append(f"Current Trends: {', '.join(context['trends'])}")
        if 'events' in context:
            formatted.append(f"Recent Events: {', '.join(context['events'])}")
        if 'discussions' in context:
            formatted.append(f"Active Discussions: {', '.join(context['discussions'])}")
        return "\n".join(formatted)

    def _extract_themes(self, content: str) -> List[str]:
        """Extract themes from generated content"""
        return [theme for theme in self.character.themes 
                if theme.lower() in content.lower()] 