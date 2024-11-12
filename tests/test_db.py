# test_db.py
import asyncio
from utils.memory_system import MemorySystem
from config.settings import Settings

async def test_connection():
    settings = Settings()
    memory_system = MemorySystem(settings.mongodb_uri)
    
    # Test storing a memory
    result = await memory_system.store_memory({
        'content': 'Test memory',
        'type': 'test'
    })
    print(f"Store result: {result}")
    
    # Test retrieving memories
    memories = await memory_system.get_memories({'type': 'test'})
    print(f"Retrieved memories: {memories}")

if __name__ == "__main__":
    asyncio.run(test_connection())