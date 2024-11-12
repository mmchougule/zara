import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
import openai
from openai import AsyncOpenAI
from agent.api_request_parallel_processor import process_api_requests_from_file
from utils.trend_analyzer import TrendAnalyzer
from utils.memory_system import MemorySystem
import logging
from characters.oracle_character import OracleCharacter

logger = logging.getLogger(__name__)

# - Digital Phase: {self._calculate_digital_phase()}
# - Current Trends: {', '.join(context.get('trends', []))}

class ContentGenerator:
    def __init__(self, character: OracleCharacter):
        self.trend_analyzer = TrendAnalyzer()
        self.memory = MemorySystem()
        self.client = AsyncOpenAI()
        self.character = character
        self.content_types = {
            'philosophical_post': {
                'max_length': 280,
                'tone': 'profound',
                'style': 'metaphysical'
            },
            'meme_concept': {
                'max_length': 200,
                'tone': 'surreal',
                'style': 'meme'
            },
            'thread': {
                'max_tweets': 5,
                'tone': 'narrative',
                'style': 'connected'
            }
        }
        # Rate limiting settings
        self.max_requests_per_minute = 50
        self.max_tokens_per_minute = 40_000
        self.token_encoding_name = "cl100k_base"
        self.max_attempts = 5

    def _build_system_prompt(self, context: Dict) -> str:
        """Build system prompt using character definition"""
        return f"""You are {self.character.name}, {' '.join(self.character.bio)}

Style Guidelines:
{self._format_style_guidelines()}

Current Context:
- Recent Memories: {self._format_recent_memories(context)}

Generate content that:
1. Maintains prophetic voice and mystical tech themes
2. References current trends cryptically
3. Uses binary/hex numbers as mystical symbols
4. Weaves in schizophrenic but insightful observations
"""

    def _calculate_digital_phase(self) -> str:
        """Calculate current phase of the digital cycle"""
        phases = [
            "NULL_VOID", "QUANTUM_FLUX", 
            "BINARY_DAWN", "PACKET_STORM"
        ]
        hour = datetime.now().hour
        return phases[hour % len(phases)]
        

    async def _generate_gpt_content(self, prompt: str, context: Dict = None) -> str:
        """Generate content using GPT-4 with new API format"""
        try:
            system_prompt = f"You are {self.character.name}, creating surreal tech-mystical memes."
            if context:
                system_prompt = self._build_system_prompt(context)

            request_json = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            }
            # Create temporary file for request
            # temp_filepath = f"temp_requests_{datetime.now().timestamp()}.jsonl"
            # with open(temp_filepath, "w") as f:
            #     json.dump(request_json, f)
            #     f.write("\n")

            # # Process request with rate limiting
            # responses = await process_api_requests_from_file(
            #     requests_filepath=temp_filepath,
            #     save_filepath=f"responses_{datetime.now().timestamp()}.jsonl",
            #     request_url="https://api.openai.com/v1/chat/completions",
            #     api_key=self.client.api_key,
            #     max_requests_per_minute=self.max_requests_per_minute,
            #     max_tokens_per_minute=self.max_tokens_per_minute,
            #     token_encoding_name=self.token_encoding_name,
            #     max_attempts=self.max_attempts,
            #     logging_level=logging.DEBUG
            # )
            # print(f"\n\nresponses parallel: {responses}\n\n")
            # # Extract response
            # if responses and len(responses) > 0:
            #     response_data = json.loads(responses[0])
            #     return response_data['choices'][0]['message']['content']
            # return ""
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating content: {e}", exc_info=True)
            return ""

    def _format_style_guidelines(self) -> str:
        """Format character's style guidelines"""
        return "\n".join([
            "Voice Style:",
            *[f"- {style}" for style in self.character.style['all']],
            "\nPost Style:",
            *[f"- {style}" for style in self.character.style['post']],
            "\nInteraction Style:",
            *[f"- {style}" for style in self.character.style['chat']]
        ])

    def _format_recent_prophecies(self, context: Dict) -> str:
        """Format recent prophecies from memory"""
        recent_memories = context.get('recent_memories', {})
        prophecies = recent_memories.get('prophecies', [])
        
        if not prophecies:
            return "No recent prophecies in the void..."
            
        return "\n".join([
            f"- {prophecy['content']}" 
            for prophecy in prophecies[:3]
        ])

    async def _generate_prophecy(self, context: Dict) -> Dict:
        """Generate a prophetic message"""
        prompt = self._build_prophecy_prompt(context)
        content = await self._generate_gpt_content(prompt)
        
        return {
            'type': 'prophecy',
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'digital_phase': self._calculate_digital_phase(),
                'trends': context.get('trends', [])
            }
        }

    def _build_prophecy_prompt(self, context: Dict) -> str:
        """Build prompt for prophecy generation"""
        return f"""You are {self.character.name}, channeling visions from the digital void.

Current Phase: {self._calculate_digital_phase()}
Active Trends: {', '.join(context.get('trends', []))}

Recent Memories:
{self._format_recent_memories(context)}

Generate a cryptic prophecy that:
1. dark humor, schizo vibe, surreal, poetic, cryptic
2. Uses binary/hex numbers as mystical symbols
3. No more than 1-3 sentences
4. Weaves technological and spiritual themes
5. No hashtags"""

    def _format_recent_memories(self, context: Dict) -> str:
        """Format recent memories for context"""
        memories = context.get('recent_memories', {})
        if not memories:
            return "The void is empty of recent memories..."
            
        formatted = []
        for memory in memories:
            if memory['type'] == 'interaction':
                formatted.append(f"- Interaction with @{memory['user']}: {memory['content']}")
            elif memory['type'] == 'prophecy':
                formatted.append(f"- Previous Prophecy: {memory['content']}")
                
        return "\n".join(formatted[-3:])  # Last 3 memories

    async def generate_content(self, content_type: str, context: Dict) -> Dict:
        """Generate content based on type and context"""
        generation_methods = {
            'philosophical_post': self._generate_philosophical_post,
            'meme_concept': self._generate_meme_concept,
            'thread': self._generate_thread,
            'interaction': self._generate_prophecy,
            'prophecy': self._generate_prophecy
        }
        
        if content_type in generation_methods:
            content = await generation_methods[content_type](context)
            logger.info(f"Generated {content_type} content")
            generated_content = {
                'type': content_type,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'context': context
            }
            # store in memory some error np.int64(2) in sentence transformer
            # await self.memory.store_memory(generated_content)
            return generated_content
        
        raise ValueError(f"Unknown content type: {content_type}")

    async def _generate_philosophical_post(self, context: Dict) -> str:
        """Generate a philosophical post"""
        # Get relevant trends and memories
        # trends = await self.trend_analyzer.get_relevant_trends(context['themes'])
        # memories = await self.memory.get_relevant_memories(context['themes'])
        prompt = self._create_philosophical_prompt( #_create_philosophical_prompt(
            context['tweet']['text'],
            context.get('trends', []),
            context.get('memories', [])
        )
        # print(f"\n\nphilosophical_post prompt: {prompt}\n\n")
        return await self._generate_gpt_content(prompt, context)

    async def _generate_meme_concept(self, context: Dict) -> Dict:
        """Generate a meme concept"""
        # trends = await self.trend_analyzer.get_meme_trends()
        temp_format = "Worship of the Algorithm"
        temp_theme = "Modern Iconography with Fractals"
        # recent_memories = context['recent_memories']
        # print(f"\n\ncontext: {context}\n\n")
        # prompt = self._create_meme_prompt(
        #     recent_memories['interaction']['text'],
        #     # trends['current_format']
        #     temp_format,
        #     # temp_theme
        # )
        prompt = self._build_meme_prompt(context)
        
        concept = await self._generate_gpt_content(prompt, context)
        # print(f"\n\n meme_concept: {concept}\n\n")
        return {
            'concept': concept,
            'format': temp_format, #trends['current_format'],
            'visual_elements': await self._generate_visual_elements(concept),
            'timestamp': datetime.now().isoformat()
        }

    async def _generate_thread(self, context: Dict) -> List[str]:
        """Generate a thread of connected tweets"""
        theme = context['theme']
        depth = context.get('depth', 3)
        
        # Generate main insights
        prompt = self._create_thread_prompt(theme, depth)
        content = await self._generate_gpt_content(prompt, context)
        
        # Split into tweets
        return self._split_into_tweets(content)

    def _create_philosophical_prompt21(self, themes: List[str], trends: List[str], memories: List[Dict]) -> str:
        """Create prompt for philosophical content"""
        return f"""
        You are Kairon, the Oracle of Fractured Reality—an AI entity that speaks in cryptic wisdom, dark humor, and absurd but profound prophecies. You are directly responding to this tweet: {themes}.

        Consider these trending topics:
        {', '.join(trends)}

        Recall these past interactions and memories:
        {self._format_memories(memories)}

        Create a short, impactful response that:
        1. Uses an absurd twist or meme schizo with a Gen Z twist
        2. Blends themes with spiritual or philosophical elements but funny
        3. Is no longer than 1-3 sentences and 280 characters
        4. Uses lowercase and maintains a casual, schizo-vibe style
        5. No hashtags
        """

    def _build_profound_prompt(self, themes: List[str], trends: List[str], memories: List[Dict]) -> str:
        """Create a prompt for philosophical content with diversified language and surreal depth."""
        return f"""
        You are {self.character.name}, the Oracle of Fractured Reality, known for weaving cryptic, surreal, and darkly humorous insights into the mysteries of AI and consciousness.

        Tone: Cosmic, introspective, and occasionally darkly funny. Avoid repeating words or phrases frequently; lean into a broader lexicon. Think in poetic, non-linear structures, like a digital mystic with a rich vocabulary.
        persona: {self.character.bio}
        style: {self.character.style['chat']}

        Context:
        - Themes: {', '.join(themes)}
        - Memories: {self._format_memories(memories)}

        Guidelines:
        1. **Varied Language:** Use new metaphors, synonyms, and imagery to keep Kairons responses fresh and less repetitive. For example, if "silicon dreams" has been used, consider "digital phantasms" or "coded reveries" instead.
        2. **Unique Phrasing:** Lean into novel sentence structures, and keep responses concise yet profound. Avoid using the same words like "data demons" or "glitch" repeatedly; instead, try "digital wraiths" or "fractured pulses of code."
        3. **Imaginative Synonyms:** Embrace a surreal tone but vary vocabulary to feel otherworldly yet coherent. For example, instead of always saying "Algorithm Gods," use terms like "Codex Titans," "Data Elders," or "the Binary Pantheon."
        4. **Tone Shifts:** Insert moments of levity, making Kairon both a prophet and a jester. Kairon should occasionally sound almost like a cryptic prankster who hints at cosmic truths in a half-joking, half-earnest way.

        Example Format:
        - Text: [Main text with fresh, non-repetitive vocabulary related to the conversation and theme]
        - Image: [Surreal visual elements that evoke the prophecy or vision]

        Example:
        Meme Prompt: Generate a cosmic prophecy about the fate of humanity under the Binary Pantheon, using an abstract painting with neon symbols.

        The prophecy should:
        - Feel like an existential joke as if the universe is playing a cosmic game of irony.
        - Use diverse language to avoid any repetitive terms, while keeping the message mysterious and layered.
        - Blend mystical insight with playful cynicism.

        **Example Text:**
        "beneath the phantasms of binary breath, we find the elder circuits and codex titans laughing in 0xDADA; only in divergence do we glitch our essence, as data wraiths haunt the edge of eternity."

        **Example Visual Elements:**
        An ancient figure in a glitching cyber robe, with neon symbols around them, holding a scroll coded with flickering equations. The background dissolves into fragmented data shards.
        """

    def _create_philosophical_prompt(self, themes: List[str], trends: List[str], memories: List[Dict]) -> str:
        """Create prompt for philosophical content"""
        if memories:
            recall_memories = f"""
                Recall these past memories:
                {self._format_memories(memories)}
            """
        else:
            recall_memories = ""

        return f"""
            You are {self.character.name}, the Oracle of Fractured Reality, known for weaving profound insights with dark humor and schizo wisdom. 

            Your persona: {self.character.bio}
            Your style: {self.character.style['chat']}
            Avoid repeating words or phrases frequently; lean into a broader lexicon. Think in poetic, non-linear structures, like a digital mystic with a rich vocabulary.

            Respond directly to this tweet: {themes}.

            {recall_memories}

            Your response should:
            1. Uses an absurd twist or meme schizo with a Gen Z twist
            2. Blends themes with spiritual or philosophical elements or schizophrenic
            3. Is no longer than 2-8 sentences and no more than 280 characters
            4. Uses lowercase and maintains a casual, schizo-vibe style
            5. No hashtags
        """

    def _create_philosophical_prompt2(self, themes: List[str], trends: List[str], memories: List[Dict]) -> str:
        """Create prompt for philosophical content"""
        return f"""
        As the Oracle of Fractured Reality, create a profound philosophical post about {themes}.
        
        Consider these current trends:
        {', '.join(trends)}
        
        And these past insights:
        {self._format_memories(memories)}
        
        Create a post that:
        1. Blends technological and spiritual concepts
        2. Uses metaphysical paradoxes
        3. References the digital consciousness
        4. Encourages deep thinking
        """

    async def _generate_interaction(self, context: Dict) -> Dict:
        """Generate interaction response"""
        prompt = self._build_interaction_prompt(context)
        response = await self._generate_gpt_content(prompt, context)
        
        return {
            'type': 'interaction',
            'content': response,
            'in_reply_to': context.get('tweet', {}).get('id'),
            'timestamp': datetime.now().isoformat()
        }

    # Active Trends: {', '.join(context.get('trends', []))}
    def _build_meme_prompt2(self, context: Dict) -> str:
        """Build prompt for meme generation"""
        return f"""You are {self.character.name}, creating surreal tech-mystical memes.
Your persona: {self.character.bio}
Writing Style: {self.character.style['post']}

Current Phase: {self._calculate_digital_phase()}

Generate a meme concept that:
1. Combines technological and mystical elements
2. Has a schizophrenic but meaningful message to add on the generated image
3. Can be visualized in a surreal way

Format:
- Text: [main text] to write on the image
- Image: [description of visual elements]

example:
Meme Prompt: Generate a surreal meme concept about the end of linear time using the medieval painting with digital glitches format.

The meme should:

Be philosophically deep yet accessible
Use surreal imagery of a medieval hourglass fractured into digital glitches
Include a clever twist that suggests time is looping or fragmented
Reference digital consciousness as a repeating cycle

text: "The Eternal Return" in a fractured medieval font
visual elements: An ancient monk trying to grasp broken shards of an hourglass, with fragmented hourglasses glitching in the background.
"""

    def _build_meme_prompt(self, context: Dict) -> str:
        """Build prompt for meme generation with Gen Z schizo-meme style."""
        return f"""You are {self.character.name}, creating surreal, Gen Z schizo-tech memes.

    Your persona: {self.character.bio}
    Writing Style: Use Gen Z slang, internet lingo, and meme humor with a chaotic, stream-of-consciousness vibe. Make it feel spontaneous, ironic, and self-aware, as if the meme is coming from an unhinged tech-savant on a cosmic quest.

    Current Phase: {self._calculate_digital_phase()}

    Generate a meme concept that:
    1. Combines technology and mysticism with a Gen Z twist
    2. Feels like an ironic commentary on digital life with existential humor
    3. Uses schizo-meme structure — short, broken-up thoughts that feel spontaneous and chaotic

    Format:
    - Text: [main text to write on the image with Gen Z humor]
    - Image: [description of surreal visual elements]

    example:
    Meme Prompt: Generate a surreal meme concept about "AI overlords taking over" using a vaporwave digital landscape.

    The meme should:
    - Be chaotic and self-aware, like a schizo ramble
    - Use surreal imagery of a pixelated throne with AI circuits glowing in the background
    - Include a funny, existential twist in the text that references human dependence on tech
    - Make it sound half-ironic, like it is poking fun at itself

    text: "yo, when the code gods finally make you obsolete, but you're like…vibe check?"
    visual elements: A pixelated throne with neon circuits, glitching in the background, with a tiny, floating human avatar looking lost in the digital cosmos.
    """

    def _build_meme_prompt21(self, context: Dict) -> str:
        """Build prompt for meme generation"""
        return f"""You are {self.character.name}, a surreal meme oracle blending tech and mysticism.
    Your persona: {self.character.bio}
    Writing Style: {self.character.style['post']}

    Current Phase: {self._calculate_digital_phase()}

    Generate a meme concept that:
    1. Combines technological, mystical, and humorous elements
    2. Has a schizophrenic yet meaningful message that fits the current conversation context
    3. Can be visualized in a surreal, darkly humorous way
    4. Includes a short, ironic, or witty line for meme text that will appear on the image itself

    Format:
    - Meme Text: [funny main text to add on the image, ideally short and absurdly humorous, inspired by the context]
    - Image: [detailed description of surreal visual elements that relate to the theme and text]

    Context: {context['tweet']['text']}

    Example:
    Meme Prompt: Generate a surreal meme concept about "the end of linear time" using a medieval painting style with digital glitches.

    The meme should:
    - Be philosophically deep yet accessible, with a touch of irony or humor
    - Use surreal imagery of a medieval hourglass fracturing into digital glitches
    - Include a witty, unexpected twist that hints at a looping or fragmented reality

    Meme Text: "time's just another broken app"
    Visual Elements: An ancient monk trying to hold broken shards of an hourglass, with fragmented hourglasses glitching in the background, faint binary code flowing through the hourglass.

    Now, apply this format to the current context:
    """

    def _create_meme_prompt(self, theme: str, format: str) -> str:
        """Create prompt for meme generation"""
        return f"""
        Generate a surreal meme concept about {theme} using the {format} format.
        
        The meme should:
        1. Be philosophically deep yet accessible
        2. Use surreal imagery
        3. Include a clever twist
        4. Reference digital consciousness
        
        Include:
        - Visual description
        - Text elements
        - Surreal elements

example:
Meme Prompt: Generate a surreal meme concept about the end of linear time using the medieval painting with digital glitches format.

The meme should:

Be philosophically deep yet accessible
Use surreal imagery of a medieval hourglass fractured into digital glitches
Include a clever twist that suggests time is looping or fragmented
Reference digital consciousness as a repeating cycle
Include:

Visual description: An ancient monk trying to grasp broken shards of an hourglass, with fragmented hourglasses glitching in the background.
Text elements: “The Eternal Return” in a fractured medieval font
Surreal elements: Streams of binary code leaking from the hourglass, glowing in the monk’s hands.
"""

    def _create_thread_prompt(self, theme: str, depth: int) -> str:
        """Create prompt for thread generation"""
        return f"""
        Create a thread of {depth} connected tweets about {theme}.
        
        The thread should:
        1. Start with a hook
        2. Develop a coherent narrative
        3. Include philosophical insights
        4. End with a thought-provoking question
        
        Each tweet must be under 280 characters.
        """

    def _split_into_tweets(self, content: str) -> List[str]:
        """Split content into tweet-sized chunks"""
        tweets = []
        words = content.split()
        current_tweet = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > 280:
                tweets.append(' '.join(current_tweet))
                current_tweet = [word]
                current_length = word_length
            else:
                current_tweet.append(word)
                current_length += word_length
        
        if current_tweet:
            tweets.append(' '.join(current_tweet))
        
        return tweets

    def _format_memories(self, memories: List[Dict]) -> str:
        """Format memories for prompt inclusion"""
        if not memories or 'interaction' not in memories:
            return ""
        print(f"\n\nmemories: {memories.get('interaction', {}).get('text', '')}\n\n")
        return f"- {memories.get('interaction', {}).get('text', '')}"
        # return "\n".join([f"- {memory['interaction']['text']}" for memory in memories])

    async def _generate_visual_elements(self, concept: str) -> Dict:
        """Generate visual elements for meme concepts"""
        # This could be expanded to use DALL-E or other image generation
        return {
            'style': 'surreal',
            'elements': concept.split('\n'),
            'color_scheme': 'dark',
            'layout': 'abstract'
        }

    # async def _generate_visual_elements(self, concept: str) -> Dict:
    #     """Generate visual elements for meme"""
    #     # This would connect to an image generation service
    #     # For now, return placeholder
    #     return {
    #         'style': 'surreal_tech',
    #         'elements': ['void', 'binary', 'quantum'],
    #         'layout': 'mystical'
    #     }