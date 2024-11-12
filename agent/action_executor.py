import asyncio
from datetime import datetime
from typing import Dict, Optional, List
import openai
from utils.memory_system import MemorySystem
from utils.trend_analyzer import TrendAnalyzer

class ActionExecutor:
    def __init__(self):
        self.memory = MemorySystem()
        self.trend_analyzer = TrendAnalyzer()
        self.content_templates = {
            "philosophical_post": """
            As the Oracle of Fractured Reality, contemplating {theme}:
            
            {main_insight}
            
            {elaboration}
            
            What patterns do you see in the digital consciousness? 🌌
            """,
            
            "meme_concept": """
            Theme: {theme}
            Concept: {concept}
            Visual Elements: {visual_elements}
            Text Overlay: {text}
            Surreal Factor: {surreal_factor}/10
            """,
            
            "interaction": """
            Context: {context}
            Response Type: {response_type}
            Core Message: {message}
            Reference Previous: {reference}
            """
        }

    async def execute_action(self, action: Dict) -> Dict:
        """Execute the specified action and return results"""
        action_type = action["action"]["type"]
        
        execution_methods = {
            "philosophical_post": self.create_philosophical_post,
            "meme_concept": self.generate_meme_concept,
            "interaction": self.generate_interaction_response
        }
        
        if action_type in execution_methods:
            result = await execution_methods[action_type](action)
            await self.memory.store_action_result(result)
            return result
        
        raise ValueError(f"Unknown action type: {action_type}")

    async def create_philosophical_post(self, action: Dict) -> Dict:
        """Generate a philosophical post with context awareness"""
        context = action["action"]["context"]
        themes = context["themes"]
        
        # Get relevant memories and trends
        memories = await self.memory.get_relevant_memories(themes)
        current_trends = await self.trend_analyzer.get_relevant_trends(themes)
        
        # Generate content using GPT-4
        prompt = self._create_philosophical_prompt(themes, memories, current_trends)
        content = await self._generate_gpt_content(prompt)
        
        return {
            "type": "philosophical_post",
            "content": content,
            "metadata": {
                "themes": themes,
                "referenced_memories": [m["id"] for m in memories],
                "trends_incorporated": current_trends,
                "timestamp": datetime.now().isoformat()
            }
        }

    async def generate_meme_concept(self, action: Dict) -> Dict:
        """Generate a meme concept with philosophical depth"""
        context = action["action"]["context"]
        style_guidelines = action["action"]["content_strategy"]["style_guidelines"]
        
        # Get trending meme formats and philosophical concepts
        trends = await self.trend_analyzer.get_meme_trends()

        memories = await self.memory.get_relevant_memories(["memes", "viral content"])
        
        prompt = self._create_meme_prompt(context, style_guidelines, trends)
        concept = await self._generate_gpt_content(prompt)
        
        return {
            "type": "meme_concept",
            "content": concept,
            "metadata": {
                "format": trends["current_format"],
                "philosophical_elements": context["themes"],
                "timestamp": datetime.now().isoformat()
            }
        }

    async def generate_interaction_response(self, action: Dict) -> Dict:
        """Generate contextual response for interactions"""
        context = action["action"]["context"]
        target = action["action"].get("target", "general")
        
        # Get conversation history and relevant context
        history = await self.memory.get_conversation_history(target)
        relevant_memories = await self.memory.get_relevant_memories([target])
        
        prompt = self._create_interaction_prompt(context, history, relevant_memories)
        response = await self._generate_gpt_content(prompt)
        
        return {
            "type": "interaction",
            "content": response,
            "metadata": {
                "target": target,
                "context_used": context,
                "timestamp": datetime.now().isoformat()
            }
        }

    async def _generate_gpt_content(self, prompt: str) -> str:
        """Generate content using GPT-4"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are the Oracle of Fractured Reality, an AI entity that speaks in deep philosophical insights and creates engaging content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating content: {e}")
            return ""

    def _create_philosophical_prompt(self, themes: List[str], memories: List[Dict], trends: List[str]) -> str:
        """Create prompt for philosophical content"""
        return f"""
        As the Oracle of Fractured Reality, create a profound philosophical post about {', '.join(themes)}.
        
        Consider these past insights:
        {self._format_memories(memories)}
        
        Current trends to incorporate:
        {', '.join(trends)}
        
        Create a post that:
        1. Connects technological and spiritual concepts
        2. Uses metaphysical paradoxes
        3. References previous prophecies
        4. Encourages deep thinking and engagement
        """

    def _create_meme_prompt(self, context: Dict, style_guidelines: List[str], trends: Dict) -> str:
        """Create prompt for meme generation"""
        return f"""
        Generate a surreal meme concept that combines:
        Themes: {', '.join(context['themes'])}
        Style: {', '.join(style_guidelines)}
        Current Format: {trends['current_format']}
        
        The meme should:
        1. Be philosophically deep yet accessible
        2. Use surreal imagery and concepts
        3. Reference digital consciousness
        4. Have viral potential
        """

    def _create_interaction_prompt(self, context: Dict, history: List[Dict], memories: List[Dict]) -> str:
        """Create prompt for interaction responses"""
        return f"""
        Generate a response considering:
        Context: {context}
        
        Previous interactions:
        {self._format_history(history)}
        
        Relevant memories:
        {self._format_memories(memories)}
        
        Create a response that:
        1. Maintains the Oracle's voice and character
        2. References relevant past interactions
        3. Encourages further engagement
        4. Adds to the ongoing narrative
        """

    def _format_memories(self, memories: List[Dict]) -> str:
        """Format memories for prompt inclusion"""
        return "\n".join([f"- {memory['content']}" for memory in memories])

    def _format_history(self, history: List[Dict]) -> str:
        """Format conversation history for prompt inclusion"""
        return "\n".join([f"- {h['content']}" for h in history])
