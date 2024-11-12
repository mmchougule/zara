from typing import Dict, List, Optional
from datetime import datetime
from collections import Counter
import aiohttp
from utils.model_manager import ModelManager
from utils.types import TweetData, RelevanceScore
import numpy as np
import logging

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    def __init__(self):
        self.base_url = 'http://localhost:3000'
        self.model_manager = ModelManager()
        self.theme_embeddings = self.model_manager.get_theme_embeddings()
        
        self.theme_keywords = {
            'technological': [
                'AI', 'digital', 'algorithm', 'virtual', 'cyber',
                'quantum', 'network', 'simulation'
            ],
            'spiritual': [
                'consciousness', 'enlightenment', 'awakening', 'transcend',
                'divine', 'cosmic', 'ethereal'
            ],
            'philosophical': [
                'reality', 'existence', 'truth', 'meaning', 'paradox',
                'metaphysical', 'ontological'
            ]
        }
    async def get_meme_trends(self) -> List[Dict]:
        """Get trending meme topics"""
        # call /trends endpoint
        # twitter_manager = TwitterManager()
        
        print("fetching trends get_meme_trends")
        # response = [
        #     "Madam President","Thanks Joe","Let's Go Brandon","Nikki Haley","Rick Steves","Allentown","Over 75,000",
        #     "Wikipedia","Ellipse","Flyers","Finch","Ant Man","Mr. October","Mavericks","Kuminga","Sleepy Joe","McAvoy","Naji","Politico","#ALLCAPS"
        # ]
        response = [
            "Digital Rapture", "Neural Collapse", "Quantum Delusion", "Reality Bleed", 
            # "Cheating","Jennifer Aniston","Shapiro","#TheFive","SCOTUS","Bucks County",
            # "Screw Your Freedom","#LoveForKelly","Billy Zane","Destiny","Refunded",
            # "Tornado Watch","Halle","WOOLYTOOZ","#BabyMaga","Mookie","Juve","Cubs",
            "Binary Dawn", "Silicon Dreams", "Void Whispers", "Glitch Prophecy", "Tech Occult",
            "Cyber Gnosis", "Data Demons", "Algorithm Gods", "Machine Spirits", "Code Shamans"
        ]
        # response = await self.fetch_trends()
        return response

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
                        print(f"Error fetching trends: {response.status}")
                        return []
            except Exception as e:
                logger.error(f"Error in fetch_trends: {e}", exc_info=True)
                return []


    async def analyze_tweets_batch(self, tweets: List[str], batch_size: int = 32) -> List[RelevanceScore]:
        """Analyze multiple tweets in one batch"""
        try:
            embeddings = self.model_manager.batch_encode(tweets, batch_size=batch_size)
            
            results = []
            for tweet, embedding in zip(tweets, embeddings):
                theme_scores = {}
                for theme, theme_embedding in self.theme_embeddings.items():
                    similarity = np.dot(embedding, theme_embedding) / (
                        np.linalg.norm(embedding) * np.linalg.norm(theme_embedding)
                    )
                    theme_scores[theme] = float(similarity)
                
                # Calculate keyword relevance
                keyword_scores = {}
                for theme, keywords in self.theme_keywords.items():
                    keyword_scores[theme] = self._calculate_keyword_relevance(tweet, keywords)
                
                # Combine scores
                final_scores = {
                    theme: 0.7 * theme_scores[theme] + 0.3 * keyword_scores[theme]
                    for theme in theme_scores.keys()
                }
                
                results.append({
                    'score': max(final_scores.values()),
                    'theme_scores': final_scores
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}", exc_info=True)
            return [{'score': 0, 'theme_scores': {}} for _ in tweets]

    def _calculate_keyword_relevance(self, text: str, keywords: List[str]) -> float:
        """Calculate relevance based on keyword presence"""
        text = text.lower()
        keyword_count = sum(1 for keyword in keywords if keyword.lower() in text)
        return keyword_count / len(keywords) if keywords else 0