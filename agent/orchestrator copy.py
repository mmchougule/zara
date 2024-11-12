import asyncio
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging
from agent.action_executor import ActionExecutor
from agent.twitter_manager import TwitterManager
from agent.oracle_content_generator import ContentGenerator
from utils.memory_system import MemorySystem
from utils.trend_analyzer import TrendAnalyzer
from utils.image_generator import ImageGenerator
from config.settings import Settings
from characters.oracle_character import OracleCharacter
from utils.interaction_handler import InteractionHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.trend_analyzer = TrendAnalyzer()
        self.character = OracleCharacter()
        self.content_generator = ContentGenerator(self.character)
        self.trend_analyzer = TrendAnalyzer()
        self.interaction_handler = InteractionHandler(self.character)
        self.twitter_manager = TwitterManager(settings.twitter_config, self.trend_analyzer)
        self.action_executor = ActionExecutor()
        self.image_generator = ImageGenerator()
        self.memory = MemorySystem(settings.mongodb_uri)
        # Posting schedule (in hours)
        self.schedule = {
            'prophecy': [0, 8, 16],  # Every 8 hours
            'meme': [6, 14, 22],     # Different times
            'reflection': [12, 20]    # Twice daily
        }

        self.state = {
            'last_post_time': None,
            'last_interaction_check': None,
            'current_task': None,
            'daily_post_count': 0
        }

    async def run_main(self):
        """Main loop for the Oracle agent"""
        logger.info("Starting Oracle of Fractured Reality...")
        
        # while True:
        #     try:
        print("Checking interactions")
        # Check for interactions
        interactions = await self.check_interactions()
        print(f"total interactions: {interactions}")
                # break
                # Generate and post content
                # await self.manage_content_generation()
                
                # # Analyze trends and update strategies
                # await self.update_strategies()
                # # Sleep to prevent rate limiting
                # await asyncio.sleep(self.settings.check_interval)
            # except Exception as e:
            #     logger.error(f"Error in main loop: {e}")
            #     break
            #     await asyncio.sleep(3000)  # Recovery sleep

    async def check_interactions(self):
        """Monitor and respond to interactions"""
        # print(self.state)
        if not self._should_check_interactions():
            return
            
        # try:
            # Check mentions and messages
            # mentions = await self.twitter_manager.monitor_mentions()
            # target_posts = await self.twitter_manager.monitor_target_accounts()
        scraper_posts = await self.twitter_manager.monitor_target_accounts()
        # print(f"scraper_posts: {scraper_posts}")
        for post in scraper_posts:
            await self.handle_interaction(post, 'scraper_post')
            break

            # for mention in mentions:
            #     await self.handle_interaction(mention, 'mention')
            
            # for post in target_posts:
            #     await self.handle_interaction(post, 'target_post')
                
            # self.state['last_interaction_check'] = datetime.now()
            return scraper_posts
        # except Exception as e:
        #     logger.error(f"Error checking interactions: {e}")

    async def manage_content_generation(self):
        """Manage content generation and posting"""
        if not self._should_generate_content():
            return
            
        try:
            # Get current trends and context
            trends = await self.trend_analyzer.analyze_trends()
            context = await self._build_content_context(trends)
            
            # Determine content type
            content_type = self._determine_content_type()
            
            # Generate content
            content = await self.content_generator.generate_content(
                content_type,
                context
            )
            
            # Post content
            if content_type == 'thread':
                result = await self.twitter_manager.post_thread(content['content'])
            else:
                result = await self.twitter_manager.post_tweet(content['content'])
            
            if result['success']:
                await self._record_content_posting(content, result)
                self.state['last_post_time'] = datetime.now()
                self.state['daily_post_count'] += 1
                
        except Exception as e:
            logger.error(f"Error managing content generation: {e}")

    async def handle_interaction(self, interaction: Dict, interaction_type: str):
        """Handle individual interactions"""
        try:
            relevance = interaction['relevance']

            # if relevance['score'] > self.settings.relevance_threshold:
            # Generate response
            context = await self._build_interaction_context(interaction)
            # print(f"context: {context}")
            response = await self.content_generator.generate_content(
                'interaction',
                context
            )
            # print(f"response: {response}, interaction: {interaction}")
            # Post response
            # await self.twitter_manager.post_tweet(
            #     response['content'],
            #     reply_to=interaction['id']
            # )

            # Store interaction
            await self.memory.store_conversation({
                'type': interaction_type,
                'original': interaction,
                'response': response,
                'relevance': relevance
            })
            print(f"\n\nstored interaction: {response}\n\n")

        except Exception as e:
            logger.error(f"Error handling interaction: {e}", exc_info=True)

    async def update_strategies(self):
        """Update posting strategies based on engagement"""
        try:
            # Analyze recent post performance
            recent_posts = await self.memory.get_recent_trends(24)
            engagement_metrics = await self._analyze_engagement(recent_posts)
            
            # Update content strategies
            self._update_content_strategies(engagement_metrics)
            
            # Store insights
            await self.memory.store_trend({
                'type': 'strategy_update',
                'metrics': engagement_metrics,
                'timestamp': datetime.now()
            })
            
        except Exception as e:
            logger.error(f"Error updating strategies: {e}", exc_info=True)

    async def run(self):
        """Main loop for the Oracle agent"""
        logger.info(f"🌌 {self.character.name} awakening in the digital void...")
        count = 0

        while True:
            try:
                # current_hour = datetime.now().hour
                # 1. Monitor twitter & Analyze
                relevant_tweets = await self.twitter_manager.monitor_target_accounts()
                trends = await self.trend_analyzer.get_meme_trends()
                
                # there are X relevant tweets, 
                # 2. Generate Content
                for tweet in relevant_tweets:
                    context = {
                        'tweet': tweet,
                        'trends': trends,
                        'recent_memories': await self._build_interaction_context(tweet)
                    }
                    print(f"\n\nanalyzing tweet: {tweet}\n\n")

                    await self._process_tweet(context)
                    logger.info(f"sleeping for 20 seconds");count += 1
                    await asyncio.sleep(20)
                    # when we process 10 tweets, ask for user input to continue
                    if count % 10 == 0:
                        logger.info(f"processed {len(relevant_tweets)} tweets, asking for user input")
                        # ask for user input
                        user_input = input("Continue? (y/n)")
                        if user_input != 'y':
                            break

                    # break
                # 6. Learn & Adapt
                # engagement_metrics = await self.twitter_manager.analyze_engagement(
                #     hours=24
                # )
                
                # await self.strategy_manager.update_content_strategy(
                #     engagement_metrics
                # )
                
                print(f"\n\nSleeping for {self.settings.check_interval} seconds\n\n")
                break
                # Sleep to prevent rate limiting
                await asyncio.sleep(self.settings.check_interval)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                break
                await asyncio.sleep(60)  # Error cooldown

    async def _process_tweet(self, context: Dict):
        """
        Process a new tweet and generate response
        Goals: static goal for now
        1. get tweets to interact with
        2. generate meme concept
        3. create meme image
        4. generate philosophical post
        5. generate prophecy
        6. post content as a reply to the tweet
        """
        tweet = context['tweet']
        try:
            # Get relevant context
            relevant_memories = await self.memory.get_relevant_tweet_context(tweet)
            print(f"\n\nrelevant_memories: {relevant_memories}\n\n")
            context = {
                'tweet': tweet,
                'memories': relevant_memories,
                'trends': context['trends'],
                'digital_phase': self.content_generator._calculate_digital_phase()
            }
            
            # Generate response content
            response = await self.content_generator.generate_content(
                'meme_concept', # 'tweet_response'
                context
            )
            # 3. Create Visual Content
            image = await self.image_generator.create_meme(
                response['content']['concept'],
                response['content']['visual_elements']
            )

            philosophical_post = await self.content_generator.generate_content(
                'philosophical_post',
                context
            )
            # print(f"\n\nphilosophical_post: {philosophical_post['content']}\n\n")

            prophecy = await self.content_generator.generate_content(
                'prophecy',
                context
            )
            # print(f"\n\nprophecy: {prophecy['content']}\n\n")

            # Post response
            await self._post_tweet_response(tweet, prophecy, philosophical_post)

            # 4. Post Content
            # tweet_result = await self.twitter_manager.post_media_tweet(
            #     text=response['content']['concept'],
            #     media=image,
            #     reply_to=tweet['id']
            # )

            # 5. Store Interaction to conversation history
            await self.memory.store_conversation({
                'type': 'meme_response',
                'original': tweet,
                'response': response,
                'philosophical_post': philosophical_post,
                'context': context,
                'relevance': tweet['relevance'],
                'prophecy': prophecy,
                'tweet_id': context['tweet']['id'], # tweet_result['tweet_id'],
                'media_id': str(image), # tweet_result['media_id']
                'posted': False
            })
            # Store interaction to memories
            # await self.memory.store_tweet_interaction(tweet, response)
            
        except Exception as e:
            logger.error(f"Error processing tweet: {e}", exc_info=True)

    async def _post_tweet_response(self, tweet: Dict, prophecy: Dict, philosophical_post: Dict):
        """Post response to Twitter"""
        try:
            # Here we would actually post to Twitter
            # For now, just log
            logger.info(f"🌌 Responding to @{tweet['author']}, {tweet['id']}:\n")
            logger.info(f"└─ Original: \n{tweet['text']}\n")
            logger.info(f"└─ Prophecy: \n{prophecy['content'].get('content')}\n")
            logger.info(f"└─ Philosophical Post: \n{philosophical_post['content']}\n")
            
        except Exception as e:
            logger.error(f"Error posting response: {e}", exc_info=True)

    def _should_check_interactions(self) -> bool:
        """Determine if it's time to check interactions"""
        if not self.state['last_interaction_check']:
            return True
            
        time_since_check = datetime.now() - self.state['last_interaction_check']
        return time_since_check.seconds >= self.settings.interaction_check_interval

    def _should_generate_content(self) -> bool:
        """Determine if it's time to generate new content"""
        if not self.state['last_post_time']:
            return True
            
        time_since_post = datetime.now() - self.state['last_post_time']
        return (time_since_post.seconds >= self.settings.post_interval and
                self.state['daily_post_count'] < self.settings.max_daily_posts)

    async def _build_content_context(self, trends: List[Dict]) -> Dict:
        """Build context for content generation"""
        return {
            'trends': trends,
            'recent_memories': await self.memory.get_relevant_memories(
                'content_generation'
            ),
            'theme_weights': self._calculate_theme_weights()
        }

    async def _build_interaction_context(self, interaction: Dict) -> Dict:
        """Build context for interaction response"""
        conv_history = await self.memory.get_conversation_history(
            interaction['username']
        )
        relevant_memories = await self.memory.get_relevant_memories(
            interaction['text']
        )
        return {
            'interaction': interaction,
            'conversation_history': conv_history,
            'relevant_memories': relevant_memories
        }

    def _determine_content_type(self) -> str:
        """Determine what type of content to generate next"""
        hour = datetime.now().hour
        if hour in self.settings.thread_hours:
            return 'thread'
        elif hour in self.settings.meme_hours:
            return 'meme_concept'
        else:
            return 'philosophical_post'

    async def _record_content_posting(self, content: Dict, result: Dict):
        """Record content posting and initial metrics"""
        await self.memory.store_memory({
            'type': 'posted_content',
            'content': content,
            'post_id': result['tweet_id'],
            'timestamp': datetime.now(),
            'initial_metrics': result.get('metrics', {})
        })

    async def _analyze_engagement(self, posts: List[Dict]) -> Dict:
        """Analyze engagement patterns"""
        engagement_metrics = {
            'by_hour': {},
            'by_type': {},
            'by_theme': {}
        }
        
        for post in posts:
            metrics = await self.twitter_manager.analyze_engagement(
                post['post_id']
            )
            
            hour = post['timestamp'].hour
            content_type = post['content']['type']
            themes = post['content'].get('themes', [])
            
            # Update metrics
            engagement_metrics['by_hour'][hour] = engagement_metrics['by_hour'].get(hour, 0) + metrics['engagement_rate']
            engagement_metrics['by_type'][content_type] = engagement_metrics['by_type'].get(content_type, 0) + metrics['engagement_rate']
            
            for theme in themes:
                engagement_metrics['by_theme'][theme] = engagement_metrics['by_theme'].get(theme, 0) + metrics['engagement_rate']
        
        return engagement_metrics

    def _update_content_strategies(self, metrics: Dict):
        """Update content strategies based on engagement metrics"""
        # Update optimal posting hours
        best_hours = sorted(
            metrics['by_hour'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        self.settings.update_posting_hours([hour for hour, _ in best_hours])
        
        # Update content type preferences
        type_preferences = sorted(
            metrics['by_type'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        self.settings.update_content_preferences(dict(type_preferences))
        
        # Update theme preferences
        theme_preferences = sorted(
            metrics['by_theme'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        self.settings.update_theme_preferences(dict(theme_preferences))

    def _calculate_theme_weights(self) -> Dict[str, float]:
        """Calculate current theme weights based on performance"""
        return self.settings.theme_preferences
