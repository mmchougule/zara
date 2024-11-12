import tweepy
import logging
from typing import List, Dict
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TwitterMonitor:
    def __init__(self, config: Dict):
        self.client = tweepy.Client(
            bearer_token=config['TWITTER_BEARER_TOKEN'],
            consumer_key=config['TWITTER_API_KEY'],
            consumer_secret=config['TWITTER_API_SECRET'],
            access_token=config['TWITTER_ACCESS_TOKEN'],
            access_token_secret=config['TWITTER_ACCESS_SECRET']
        )
        self.target_accounts = ['truth_terminal', 'luna_virtuals', 'dasha_terminal', 'MirraMrr', 'PraistSol']
        self.last_check = datetime.now() - timedelta(hours=1)

    async def get_new_tweets(self) -> List[Dict]:
        """Monitor target accounts for new tweets"""
        try:
            new_tweets = []
            for account in self.target_accounts:
                user = self.client.get_user(username=account)
                tweets = self.client.get_users_tweets(
                    user.data.id,
                    max_results=10,
                    start_time=self.last_check
                )
                
                if tweets.data:
                    for tweet in tweets.data:
                        new_tweets.append({
                            'id': tweet.id,
                            'text': tweet.text,
                            'author': account,
                            'created_at': tweet.created_at
                        })
            
            self.last_check = datetime.now()
            return new_tweets
            
        except Exception as e:
            logger.error(f"Error monitoring Twitter: {e}")
            return [] 