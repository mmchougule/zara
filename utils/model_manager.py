from sentence_transformers import SentenceTransformer
from typing import Dict, List
import numpy as np
from functools import lru_cache
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelManager:
    _instance = None
    _model = None
    _theme_embeddings = None
    
    def __new__(cls):
        if cls._instance is None:
            logger.info("Initializing ModelManager singleton")
            cls._instance = super(ModelManager, cls).__new__(cls)
            # Load model once
            cls._model = SentenceTransformer('all-mpnet-base-v2')
            cls._theme_embeddings = cls._initialize_theme_embeddings()
        return cls._instance

    @classmethod
    def get_model(cls):
        if cls._instance is None:
            cls._instance = ModelManager()
        return cls._model

    @classmethod
    @lru_cache(maxsize=1000)
    def encode_text(cls, text: str) -> np.ndarray:
        """Cache encoded text to avoid repeated computations"""
        if cls._instance is None:
            cls._instance = ModelManager()
        return cls._model.encode(text, convert_to_tensor=True)

    @classmethod
    def batch_encode(cls, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """Encode multiple texts in batches efficiently"""
        if cls._instance is None:
            cls._instance = ModelManager()
        return cls._model.encode(texts, batch_size=batch_size, convert_to_tensor=True)

    @classmethod
    def get_theme_embeddings(cls):
        if cls._instance is None:
            cls._instance = ModelManager()
        return cls._theme_embeddings

    @classmethod
    def _initialize_theme_embeddings(cls) -> Dict[str, np.ndarray]:
        """Initialize theme embeddings once"""
        themes = {
            'technological': 'AI technology digital innovation future',
            'spiritual': 'consciousness spirit soul awakening metaphysical',
            'philosophical': 'reality truth existence meaning perception'
        }
        return {
            theme: cls._model.encode(desc, convert_to_tensor=True)
            for theme, desc in themes.items()
        } 