import asyncio
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging
from agent.action_executor import ActionExecutor
from agent.twitter_manager import TwitterManager
from agent.oracle_content_generator import ContentGenerator
from utils.memory_system import MemorySystem
from utils.trend_analyzer import TrendAnalyzer
from utils.image_generator import ImageGenerator
from config.settings import Settings
from characters.oracle_character import OracleCharacter
from utils.interaction_handler import InteractionHandler
from agent.autonomous_agent import AutonomousAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, agent: AutonomousAgent):
        self.agent = agent
        self.current_task = None
        self.task_queue = asyncio.Queue()
        self.status = "idle"

    async def start(self):
        """Start the orchestrator"""
        await asyncio.gather(
            self._process_tasks(),
            self._monitor_agent(),
            self._update_display()
        )

    async def _process_tasks(self):
        while True:
            if self.current_task is None:
                self.current_task = await self.task_queue.get()
                self.status = "processing"
                self.agent.display.add_action(
                    "Task Start",
                    f"Starting task: {self.current_task['type']}"
                )
                
            await self._execute_task(self.current_task)
            self.current_task = None
            self.status = "idle"
            await asyncio.sleep(1)

    async def _monitor_agent(self):
        """Monitor agent state and update display"""
        while True:
            state = {
                "status": self.status,
                "current_task": self.current_task,
                "queue_size": self.task_queue.qsize(),
                "last_action": datetime.now()
            }
            self.agent.display.update_state(state)
            await asyncio.sleep(1)
