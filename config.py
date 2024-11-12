import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'TWITTER_API_KEY': os.getenv('TWITTER_API_KEY'),
    'TWITTER_API_SECRET': os.getenv('TWITTER_API_SECRET'),
    'TWITTER_BEARER_TOKEN': os.getenv('TWITTER_BEARER_TOKEN'),
    'TWITTER_ACCESS_TOKEN': os.getenv('TWITTER_ACCESS_TOKEN'),
    'TWITTER_ACCESS_SECRET': os.getenv('TWITTER_ACCESS_SECRET'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    
    'CHECK_INTERVAL': 60,  # seconds
    'POST_INTERVAL': 3600,  # 1 hour
    'TARGET_ACCOUNTS': ['truth_terminal', 'luna_virtuals', 'dasha_terminal', 'MirraMrr', 'PraistSol']
} 