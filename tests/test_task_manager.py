import asyncio
from enhanced_task_manager import EnhancedTaskManager

async def test_task_manager():
    manager = EnhancedTaskManager()
    
    # Initialize tasks
    await manager.initialize_tasks()
    
    # Get next action
    action = await manager.get_next_strategic_action()
    print("Next Strategic Action:", action)
    
    # Update progress
    if action:
        await manager.update_task_progress({
            "action": action["action"],
            "metrics": {
                "engagement": 0.8,
                "responses": 5
            }
        })

if __name__ == "__main__":
    asyncio.run(test_task_manager())
