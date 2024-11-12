from typing import Dict
import asyncio
import yaml
import logging
from datetime import datetime
from utils.display_manager import DisplayManager
from utils.log_manager import LogManager
from agent.task_manager import TaskManager
from agent.goal_system import GoalSystem
from agent.decision_engine import DecisionEngine
from utils.trend_monitor import TrendMonitor

logger = logging.getLogger(__name__)

class AutonomousAgent:
    def __init__(self, character_config: str, tasks_config: str):
        self.configs = self._load_configs(character_config, tasks_config)
        self.log_manager = LogManager()
        self.display = DisplayManager(self.log_manager)
        self.task_manager = TaskManager(self.configs['tasks'])
        self.goal_system = GoalSystem(self.configs['tasks']['core_goals'])
        self.decision_engine = DecisionEngine(self.configs)
        self.trend_monitor = TrendMonitor(self.configs)
        # name of the agent
        self.agent_name = self.configs['character']['name']
        
        self.running = True
        self.current_state = {
            'status': 'initializing',
            'current_task': None,
            'last_action_time': None,
            'active_goals': []
        }

    def _load_configs(self, character_path: str, tasks_path: str) -> Dict:
        try:
            with open(character_path, 'r') as f:
                character_config = yaml.safe_load(f)
            with open(tasks_path, 'r') as f:
                tasks_config = yaml.safe_load(f)
            return {
                'character': character_config,
                'tasks': tasks_config
            }
        except Exception as e:
            logger.error(f"Failed to load configs: {e}")
            raise

    async def start(self):
        """Start autonomous operation"""
        self.log_manager.add_log('SYSTEM', f'Starting {self.agent_name} autonomous agent')
        self.current_state['status'] = 'running'
        
        try:
            # Start display first
            # TODO: Make this non-blocking and fix the display
            # self.display.start()

            # Start main cycles
            await asyncio.gather(
                self._run_goal_cycle(),
                self._run_task_cycle(),
                self._run_trend_cycle()
            )
            
        except Exception as e:
            self.log_manager.add_log('ERROR', f"Critical error in autonomous operation: {str(e)}")
            logger.error(f"Critical error: {e}")
        finally:
            self.running = False
            self.display.stop()
            self.log_manager.add_log('SYSTEM', f'Shutting down {self.agent_name} autonomous agent')

    async def _run_goal_cycle(self):
        """Continuously evaluate and update goals"""
        self.log_manager.add_log('SYSTEM', f'Starting goal cycle for {self.agent_name}')
        print(f'Starting goal cycle for {self.agent_name}')
        while self.running:
            try:
                self.log_manager.add_log('GOAL', f'Evaluating goals for {self.agent_name}')
                # context = await self._gather_context()
                # 
                active_goals = await self.goal_system.evaluate_goals()
                
                for goal in active_goals:
                    self.log_manager.add_log('GOAL', f"Active goal: {goal['name']}")
                    task = await self.task_manager.create_task(
                        task_type='goal_task',
                        priority=goal.get('priority', 1),
                        context={'goal': goal}
                    )
                    self.log_manager.add_log('TASK', f"Created task for goal: {task['id']}")
                
                self.current_state['active_goals'] = active_goals
                await asyncio.sleep(60)  # Check goals every minute
                
            except Exception as e:
                self.log_manager.add_log('ERROR', f"Goal cycle error: {str(e)}")
                await asyncio.sleep(30)

    async def _run_task_cycle(self):
        """Continuously process tasks"""
        while self.running:
            try:
                self.log_manager.add_log('SYSTEM', 'Checking for new tasks...')
                task = await self.task_manager.get_next_task()
                
                if not task:
                    # Create a sample task if none exists
                    task = await self.task_manager.create_task(
                        'analyze_trends',
                        priority=1,
                        context={'source': 'automatic'}
                    )
                    self.log_manager.add_log('TASK', f"Created new task: {task['type']}")
                
                if task:
                    self.log_manager.add_log('TASK', f"Processing task: {task['type']}")
                    self.current_state['current_task'] = task
                    
                    # Execute task
                    result = await self._execute_task(task)
                    await self.task_manager.complete_task(task['id'], result)
                    
                    self.log_manager.add_log('TASK', f"Completed task: {task['id']} with status: {result}")
                    self.current_state['last_action_time'] = datetime.now()
                    self.current_state['current_task'] = None
                
                await asyncio.sleep(5)  # Shorter sleep for testing
                
            except Exception as e:
                self.log_manager.add_log('ERROR', f"Task cycle error: {str(e)}")
                await asyncio.sleep(5)

    async def _run_trend_cycle(self):
        """Continuously monitor trends"""
        while self.running:
            try:
                self.log_manager.add_log('TREND', 'Starting trend analysis')
                trends = await self.trend_monitor.monitor_trends()
                
                # Log each trend category
                for category, trend_list in trends.items():
                    self.log_manager.add_log(
                        'TREND', 
                        f"Found trends in {category}: {', '.join(trend_list[:2])}"
                    )
                
                self.current_state['trends'] = trends
                await asyncio.sleep(30)  # Check trends every 30 seconds for testing
                
            except Exception as e:
                self.log_manager.add_log('ERROR', f"Trend cycle error: {str(e)}")
                await asyncio.sleep(10)

    async def _execute_task(self, task: Dict) -> Dict:
        """Execute a task"""
        try:
            self.log_manager.add_log('ACTION', f"Starting execution of task: {task['type']}")
            
            # Simulate different task types
            if task['type'] == 'analyze_trends':
                self.log_manager.add_log('ACTION', "Analyzing current trends...")
                await asyncio.sleep(2)
                self.log_manager.add_log('ACTION', "Trend analysis complete")
            elif task['type'] == 'generate_content':
                self.log_manager.add_log('ACTION', "Generating philosophical content...")
                await asyncio.sleep(3)
                self.log_manager.add_log('ACTION', "Content generation complete")
            
            return {
                'status': 'completed',
                'result': f"Successfully executed {task['type']}",
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.log_manager.add_log('ERROR', f"Task execution error: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now()
            }

    async def _gather_context(self) -> Dict:
        """Gather current context"""
        return {
            'status': self.current_state['status'],
            'current_task': self.current_state['current_task'],
            'last_action_time': self.current_state['last_action_time'],
            'active_goals': self.current_state['active_goals']
        }