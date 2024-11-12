from typing import Dict, List, Optional
from typing_extensions import TypedDict
from datetime import datetime

class TweetData(TypedDict):
    id: str
    text: str
    author: str
    created_at: datetime
    metrics: Dict[str, int]

class RelevanceScore(TypedDict):
    score: float
    theme_scores: Dict[str, float] 