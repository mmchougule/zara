import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from utils.trend_analyzer import TrendAnalyzer
from utils.memory_system import MemorySystem
import logging

logger = logging.getLogger(__name__)

class TwitterManager:
    def __init__(self, config: Dict, trend_analyzer: Optional[TrendAnalyzer] = None):
        self.base_url = config.get('api_base_url', 'http://localhost:3000')
        # Initialize Twitter API
        # auth = tweepy.OAuthHandler(
        #     config['api_key'],
        #     config['api_secret']
        # )
        # auth.set_access_token(
        #     config['access_token'],
        #     config['access_token_secret']
        # )
        # self.api = tweepy.API(auth, wait_on_rate_limit=True)
        # self.client = tweepy.Client(
        #     bearer_token=config['bearer_token'],
        #     consumer_key=config['api_key'],
        #     consumer_secret=config['api_secret'],
        #     access_token=config['access_token'],
        #     access_token_secret=config['access_token_secret']
        # )
        self.username = config.get('twitter_username', 'zaraai')
        self.config = config
        self.trend_analyzer = trend_analyzer or TrendAnalyzer()
        # self.target_accounts = config.get('target_accounts', [])

        self.memory = MemorySystem()
        
        # Target accounts to monitor
        self.target_accounts = [
            'truth_terminal',
            'luna_virtuals',
            'ai16z',
        ]
        
        # Engagement tracking
        self.engagement_metrics = {
            'likes': [],
            'retweets': [],
            'replies': [],
            'mentions': []
        }

    async def post_tweet(self, content: str, reply_to: Optional[str] = None) -> Dict:
        """Post a tweet or reply"""
        try:
            if reply_to:
                response = self.client.create_tweet(
                    text=content,
                    in_reply_to_tweet_id=reply_to
                )
            else:
                response = self.client.create_tweet(text=content)
            
            tweet_data = response.data
            
            # Store in memory
            await self.memory.store_tweet({
                'id': tweet_data['id'],
                'content': content,
                'type': 'reply' if reply_to else 'original',
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'tweet_id': tweet_data['id'],
                'content': content
            }
            
        except Exception as e:
            logger.error(f"Error posting tweet: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    async def post_thread(self, tweets: List[str]) -> Dict:
        """Post a thread of tweets"""
        try:
            thread_tweets = []
            reply_to = None
            
            for tweet in tweets:
                result = await self.post_tweet(tweet, reply_to)
                if result['success']:
                    thread_tweets.append(result['tweet_id'])
                    reply_to = result['tweet_id']
                else:
                    return {'success': False, 'error': result['error']}
            
            return {
                'success': True,
                'thread_ids': thread_tweets
            }
            
        except Exception as e:
            logger.error(f"Error posting thread: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    async def monitor_mentions(self) -> List[Dict]:
        """Monitor and process mentions"""
        try:
            mentions = self.client.get_users_mentions(
                self.username, 
                max_results=100,
                tweet_fields=['created_at', 'conversation_id']
            )
            
            processed_mentions = []
            for mention in mentions.data or []:
                # Process each mention
                mention_data = {
                    'id': mention.id,
                    'text': mention.text,
                    'author': mention.author_id,
                    'created_at': mention.created_at,
                    'conversation_id': mention.conversation_id
                }
                
                # Store in memory
                await self.memory.store_mention(mention_data)
                processed_mentions.append(mention_data)
            
            return processed_mentions
            
        except Exception as e:
            logger.error(f"Error monitoring mentions: {e}", exc_info=True)
            return []

    async def fetch_tweets(self, username: str, limit: int = 100) -> List[Dict]:
        """
        Fetch tweets from local API endpoint.
        This is used to get tweets from the database.
        A background service continuously fetches tweets and stores them in the database real-time.
        """
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/tweets/{username}/{limit}"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error fetching tweets: {response.status}")
                        return []
            except Exception as e:
                # logger.error(f"Error in fetch_tweets: {e}", exc_info=True)
                print(f"\033[91mError in fetch_tweets: {e}\033[0m")
                return []

    async def fetch_trends(self) -> List[Dict]:
        """Fetch current trends from local API endpoint"""
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/trends"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(response)
                        print(f"Error fetching trends twitter_manager: {response.status}")
                        return []
            except Exception as e:
                logger.error(f"Error in fetch_trends: {e}", exc_info=True)
                return []

    async def monitor_target_accounts(self) -> List[Dict]:
        """Monitor target accounts for relevant content"""
        try:
            all_tweets = []
            # get existing tweets from memory
            existing_tweets = await self.memory.get_tweets()
            # Collect tweets from all accounts
            for account in self.target_accounts:
                print(f"monitoring {account}")
                # this needs localhost:3000/tweets/:username api server running. commented out for now
                tweets = await self.fetch_tweets(account, 20)
                if tweets:
                    all_tweets.extend([(tweet, account) for tweet in tweets])

            if not all_tweets:
                logger.info("No tweets found to analyze")
                return []

            # filter out existing tweets
            # error here fix later
            # all_tweets = [tweet for tweet in all_tweets if tweet['original']['id'] not in existing_tweets]
            # print(f"all_tweets: {len(all_tweets)}")

            # Batch analyze all tweets
            tweet_texts = [tweet['text'] for tweet, _ in all_tweets]
            logger.info(f"Analyzing batch of {len(tweet_texts)} tweets")
            
            relevance_scores = await self.trend_analyzer.analyze_tweets_batch(tweet_texts)
            # print(f"relevance_scores: {relevance_scores}")
            # Process results
            relevant_tweets = []
            for (tweet, account), relevance in zip(all_tweets, relevance_scores):
                if relevance['score'] > 0.2:  # Adjusted threshold
                    relevant_tweets.append({
                        'id': tweet['id'],
                        'text': tweet['text'],
                        'author': account,
                        'username': tweet['username'],
                        'created_at': tweet['timeParsed'],
                        'relevance': relevance,
                        'metrics': {
                            'likes': tweet.get('likes', 0),
                            'retweets': tweet.get('retweets', 0),
                            'replies': tweet.get('replies', 0),
                            'views': tweet.get('views', 0)
                        }
                    })
            
            logger.info(f"Found {len(relevant_tweets)} relevant tweets")
            return relevant_tweets
            
        except Exception as e:
            logger.error(f"Error monitoring target accounts: {e}", exc_info=True)
            return []

    async def analyze_engagement(self, tweet_data: Dict) -> Dict:
        """Analyze engagement for a specific tweet"""
        try:
            metrics = {
                'like_count': tweet_data.get('like_count', 0),
                'retweet_count': tweet_data.get('retweet_count', 0),
                'reply_count': tweet_data.get('reply_count', 0)
            }
            
            # Store engagement metrics
            self.engagement_metrics['likes'].append(metrics['like_count'])
            self.engagement_metrics['retweets'].append(metrics['retweet_count'])
            self.engagement_metrics['replies'].append(metrics['reply_count'])
            
            return {
                'tweet_id': tweet_data['id'],
                'metrics': metrics,
                'engagement_rate': self._calculate_engagement_rate(metrics)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing engagement: {e}", exc_info=True)
            return {}

    def _calculate_engagement_rate(self, metrics: Dict) -> float:
        """Calculate engagement rate for metrics"""
        total_engagement = (
            metrics['like_count'] +
            metrics['retweet_count'] * 2 +  # Weight retweets more
            metrics['reply_count'] * 3  # Weight replies most
        )
        # Assuming follower count is stored or retrieved
        follower_count = self._get_follower_count()
        if follower_count > 0:
            return total_engagement / follower_count
        # Use a base follower count or adjust based on your needs
        base_follower_count = 1000  # Adjust this value
        return total_engagement / base_follower_count if base_follower_count > 0 else 0

    def _get_follower_count(self) -> int:
        """Get current follower count"""
        try:
            user = self.client.get_user(username=self.username)
            return user.data.public_metrics['followers_count']
        except Exception:
            return 0
