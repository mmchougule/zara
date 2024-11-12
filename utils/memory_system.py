from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import os
# from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from pymongo.collection import Collection
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

from utils.model_manager import ModelManager
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
class MemorySystem:
    def __init__(self, mongodb_uri: str = "localhost"):
        try:
            mongo_uri = os.environ.get("MONGODB_URI") or mongodb_uri
            # Initialize MongoDB connection with proper authentication
            self.client = MongoClient(mongo_uri)
            # self.client = MongoClient(
            #     mongodb_uri,
            #     serverSelectionTimeoutMS=5000,
            #     connectTimeoutMS=10000,
            #     retryWrites=True,
            #     retryReads=True
            # )

            # Test connection
            client = MongoClient(mongo_uri, server_api=ServerApi('1'))
            # Send a ping to confirm a successful connection
            try:
                client.admin.command('ping')
                print("Pinged your deployment. You successfully connected to MongoDB!")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)

            self.db = self.client.oracle
            # print(self.db.list_collection_names())
            # Collections for different types of memories
            self.memories: Collection = self.db.memories
            self.conversations: Collection = self.db.conversations
            self.trends: Collection = self.db.trends
            self.engagement: Collection = self.db.engagement

            
            # Verify connection and create collection if needed
            # self._initialize_collection()

            # Get shared model instance
            self.model_manager = ModelManager()
            self.encoder = self.model_manager.get_model()
            # Memory configuration
            self.memory_config = {
                'short_term_window': timedelta(hours=24),
                'relevance_threshold': 0.75,
                'max_memories': 1000,
                'importance_decay': 0.95  # Daily decay factor
            }
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB connection: {e}", exc_info=True)
            raise e

    async def encode_memory(self, text: str) -> np.ndarray:
        """Encode text using shared model"""
        return self.encoder.encode(text, convert_to_tensor=True).tolist()

    async def calculate_similarity(self, memory1: np.ndarray, memory2: np.ndarray) -> float:
        """Calculate cosine similarity between memory embeddings"""
        return float(np.dot(memory1, memory2) / (
            np.linalg.norm(memory1) * np.linalg.norm(memory2)
        ))


    def _initialize_collection(self):
        """Initialize collection and verify access"""
        try:
            # Try to create collection if it doesn't exist
            if 'memories' not in self.db.list_collection_names():
                self.db.create_collection('memories')
                logger.info("Created memories collection")
            
            # Verify write access with a test document
            test_doc = {
                '_id': 'test_access',
                'timestamp': datetime.now(),
                'type': 'system_test'
            }
            
            # Upsert the test document
            self.memories.update_one(
                {'_id': 'test_access'},
                {'$set': test_doc},
                upsert=True
            )
            
            # Verify read access
            test_read = self.memories.find_one({'_id': 'test_access'})
            if not test_read:
                raise Exception("Failed to verify read access")
            
            # Clean up test document
            self.memories.delete_one({'_id': 'test_access'})
            
            logger.info("Successfully verified database access")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}", exc_info=True)
            raise

    async def store_memory(self, memory: Dict) -> str:
        """Store a new memory with embeddings"""
        try:
            # Generate embedding for the memory content
            embedding = self.encoder.encode(memory['content'])
            
            memory_doc = {
                'content': memory['content'],
                'type': memory.get('type', 'general'),
                'embedding': embedding.tolist(),
                'timestamp': datetime.now().isoformat(),
                'importance': memory.get('importance', 1.0),
                'context': memory.get('context', {}),
                'metadata': memory.get('metadata', {}),
                'references': memory.get('references', []),
                'engagement': memory.get('engagement', {})
            }
            
            result = self.memories.insert_one(memory_doc)
            
            # Maintain memory limit
            await self._cleanup_old_memories()
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}", exc_info=True)
            return ""

    async def get_relevant_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """Retrieve relevant memories using semantic search"""
        try:
            # Generate embedding for query
            query_embedding = self.encoder.encode(query)
            
            # Get all memories with their embeddings
            all_memories = list(self.memories.find(
                {},
                {'content': 1, 'embedding': 1, 'importance': 1, 'timestamp': 1}
            ))
            
            if not all_memories:
                return []

            # Calculate similarity scores
            similarities = []
            for memory in all_memories:
                memory_embedding = np.array(memory['embedding'])
                similarity = np.dot(query_embedding, memory_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(memory_embedding)
                )
                
                # Apply time decay to importance
                days_old = (datetime.now() - memory['timestamp']).days
                decayed_importance = memory['importance'] * (
                    self.memory_config['importance_decay'] ** days_old
                )
                
                # Combine similarity with importance
                final_score = similarity * decayed_importance
                similarities.append((memory, final_score))
            
            # Sort by final score and get top memories
            sorted_memories = sorted(similarities, key=lambda x: x[1], reverse=True)
            return [m[0] for m in sorted_memories[:limit]]
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}", exc_info=True)
            return []

    async def store_conversation(self, conversation: Dict) -> str:
        """Store a conversation interaction"""
        # type, original, response, relevance
        # embedding = self.encoder.encode(conversation['response']['content']).tolist()
        # Extract the text content for encoding
        content_to_encode = conversation['response']['content']
        if isinstance(content_to_encode, dict):
            # If content is a dictionary, convert it to string
            content_to_encode = str(content_to_encode)
        embedding = self.encoder.encode(content_to_encode).tolist()

        try:
            conversation_doc = {
                'type': conversation['type'],
                'original': conversation['original'],
                'response': conversation['response'],
                'philosophical_post': conversation['philosophical_post'],
                'relevance': conversation['relevance'],
                'prophecy': conversation['prophecy'],
                'tweet_id': conversation['tweet_id'],
                'media_id': conversation['media_id'],
                'timestamp': datetime.now(),
                'context': conversation.get('context', {}),
                'embedding': embedding, # self.encoder.encode(conversation['content']).tolist()
            }
            result = self.conversations.insert_one(conversation_doc)
            print(f"\n\nconversation_doc result: {result}\n\n")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing conversation: {e}", exc_info=True)
            return ""

    async def get_conversation_history(self, participant: str, limit: int = 10) -> List[Dict]:
        """Retrieve conversation history with a specific participant"""
        try:
            return list(self.conversations.find(
                {'original.author': participant}
            ).sort('timestamp', -1).limit(limit))
            
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}", exc_info=True)
            # throw error
            raise e
            return []

    async def store_trend(self, trend: Dict) -> str:
        """Store a detected trend"""
        try:
            trend_doc = {
                'content': trend['content'],
                'type': trend['type'],
                'timestamp': datetime.now(),
                'strength': trend.get('strength', 1.0),
                'related_topics': trend.get('related_topics', []),
                'embedding': self.encoder.encode(trend['content']).tolist()
            }
            
            result = self.trends.insert_one(trend_doc)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing trend: {e}", exc_info=True)
            return ""

    async def get_recent_trends(self, hours: int = 24) -> List[Dict]:
        """Get recent trends within specified time window"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return list(self.trends.find(
                {'timestamp': {'$gte': cutoff_time}}
            ).sort('timestamp', -1))
            
        except Exception as e:
            logger.error(f"Error retrieving trends: {e}", exc_info=True)
            return []
    async def update_memory_importance(self, memory_id: str, engagement_score: float):
        """Update memory importance based on engagement"""
        try:
            self.memories.update_one(
                {'_id': memory_id},
                {'$set': {'importance': engagement_score}}
            )
        except Exception as e:
            logger.error(f"Error updating memory importance: {e}", exc_info=True)

    async def get_tweets(self) -> List[Dict]:
        """Get all tweets from memory"""
        # get all recent conversations timestamp > 24 hours
        cutoff_time = datetime.now() - timedelta(hours=6)
        return list(self.conversations.find(
            {'timestamp': {'$gte': cutoff_time}}
        ))

    async def _cleanup_old_memories(self):
        """Remove old memories when limit is reached"""
        try:
            total_memories = self.memories.count_documents({})
            if total_memories > self.memory_config['max_memories']:
                # Remove oldest, least important memories
                excess_count = total_memories - self.memory_config['max_memories']
                oldest_memories = self.memories.find().sort([
                    ('importance', 1),
                    ('timestamp', 1)
                ]).limit(excess_count)
                
                memory_ids = [m['_id'] for m in oldest_memories]
                self.memories.delete_many({'_id': {'$in': memory_ids}})
                
        except Exception as e:
            logger.error(f"Error cleaning up memories: {e}", exc_info=True)

    async def get_memory_statistics(self) -> Dict:
        """Get statistics about stored memories"""
        try:
            total_memories = self.memories.count_documents({})
            recent_memories = self.memories.count_documents({
                'timestamp': {'$gte': datetime.now() - self.memory_config['short_term_window']}
            })
            
            return {
                'total_memories': total_memories,
                'recent_memories': recent_memories,
                'memory_types': await self._get_memory_type_distribution()
            }
        except Exception as e:
            logger.error(f"Error getting memory statistics: {e}", exc_info=True)
            return {}

    async def _get_memory_type_distribution(self) -> Dict:
        """Get distribution of memory types"""
        try:
            pipeline = [
                {'$group': {'_id': '$type', 'count': {'$sum': 1}}}
            ]
            result = self.memories.aggregate(pipeline)
            return {doc['_id']: doc['count'] for doc in result}
        except Exception as e:
            logger.error(f"Error getting memory type distribution: {e}", exc_info=True)
            return {}

    async def store_tweet_interaction(self, tweet: Dict, response: Dict):
        """Store tweet interaction in memory"""
        try:
            embedding = await self.encode_memory(f"{tweet['text']} {response['content']}")
            
            memory = {
                'type': 'tweet_interaction',
                'tweet': tweet,
                'response': response,
                'embedding': embedding,
                'timestamp': datetime.now().isoformat()
            }
            
            # self.memories.insert_one(memory)
            logger.info(f"Stored tweet interaction: {tweet['id']}")
            
        except Exception as e:
            logger.error(f"Error storing tweet interaction: {e}", exc_info=True)

    async def get_relevant_tweet_context(self, tweet: Dict) -> List[Dict]:
        """Get relevant memories for tweet context"""
        try:
            query = tweet['text']
            query_embedding = await self.encode_memory(query)

            # Calculate similarities
            # similarities = [
            #     self._calculate_similarity(query_embedding, m['embedding'])
            #     for m in self.memories if m['type'] == 'tweet_interaction'
            # ]
            similarities = []
            # we have embeddings array in conversations collection
            # its an array of embeddings 768 dim
            for m in self.conversations.find(
                # {'original.author': tweet['original']['author']},
                {'embedding': 1}
            ):
                similarity = self.calculate_similarity(query_embedding, m['embedding'])
                similarities.append((m, similarity))
            # Get top 5 relevant memories
            top_indices = np.argsort(similarities)[-5:]
            return [self.memories[i] for i in top_indices]
            
        except Exception as e:
            logger.error(f"Error getting tweet context: {e}", exc_info=True)
            return []

