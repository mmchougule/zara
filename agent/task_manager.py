from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import uuid
import logging

logger = logging.getLogger(__name__)

class TaskManager:
    def __init__(self, config: Dict):
        self.config = config
        self.tasks: Dict[str, Dict] = {}
        self.task_queue = asyncio.Queue()
        self.completed_tasks: List[Dict] = []
        
    async def create_task(self, task_type: str, priority: int = 1, context: Dict = None) -> Dict:
        """Create a new task"""
        task = {
            'id': str(uuid.uuid4()),
            'type': task_type,
            'priority': priority,
            'context': context or {},
            'status': 'pending',
            'created_at': datetime.now(),
            'completed_at': None
        }
        
        self.tasks[task['id']] = task
        await self.task_queue.put(task)
        return task
        
    async def get_next_task(self) -> Optional[Dict]:
        """Get next task from queue"""
        if not self.task_queue.empty():
            return await self.task_queue.get()
        return None

    async def complete_task(self, task_id: str, result: Dict) -> None:
        """Mark task as completed"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['completed_at'] = datetime.now()
            self.tasks[task_id]['result'] = result
            self.completed_tasks.append(self.tasks[task_id])