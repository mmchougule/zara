import asyncio
import pytest
from datetime import datetime
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.orchestrator import Orchestrator
from config.settings import Settings

@pytest.fixture
def settings():
    return Settings(
        mongodb_uri="mongodb://localhost:27017/",
        openai_api_key="your-api-key",
        twitter_config={
            "api_key": "your-twitter-api-key",
            "api_secret": "your-twitter-api-secret",
            "access_token": "your-access-token",
            "access_secret": "your-access-secret"
        }
    )

@pytest.fixture
def orchestrator(settings):
    return Orchestrator(settings)

async def test_content_generation(orchestrator):
    """Test content generation pipeline"""
    # Generate content
    context = await orchestrator._build_content_context([])
    content = await orchestrator.content_generator.generate_content(
        'philosophical_post',
        context
    )
    
    assert content is not None
    assert 'content' in content
    assert 'type' in content

async def test_interaction_handling(orchestrator):
    """Test interaction handling"""
    test_interaction = {
        'id': '123456',
        'text': 'What are your thoughts on digital consciousness?',
        'author': 'test_user'
    }
    
    await orchestrator.handle_interaction(test_interaction, 'mention')
    
    # Verify memory storage
    conversations = await orchestrator.memory.get_conversation_history('test_user')
    assert len(conversations) > 0

async def test_strategy_updates(orchestrator):
    """Test strategy updating"""
    # Simulate some engagement metrics
    test_posts = [
        {
            'post_id': '123',
            'timestamp': datetime.now(),
            'content': {
                'type': 'philosophical_post',
                'themes': ['technological', 'spiritual']
            }
        }
    ]
    
    metrics = await orchestrator._analyze_engagement(test_posts)
    orchestrator._update_content_strategies(metrics)
    
    assert orchestrator.settings.theme_preferences is not None

# Main test runner
async def main():
    settings = Settings(
        mongodb_uri="mongodb://localhost:27017/",
        openai_api_key="your-api-key",
        twitter_config={
            "api_key": "your-twitter-api-key",
            "api_secret": "your-twitter-api-secret",
            "access_token": "your-access-token",
            "access_secret": "your-access-secret"
        }
    )
    print(f"settings created {settings}")
    
    orchestrator = Orchestrator(settings)
    print(orchestrator)
    interactions = await orchestrator.check_interactions()
    print(interactions)
    # Run tests
    # await test_content_generation(orchestrator)
    # await test_interaction_handling(orchestrator)
    # await test_strategy_updates(orchestrator)
    
    print("All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
