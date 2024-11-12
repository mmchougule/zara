from typing import Dict, List, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class Goal:
    def __init__(self, name: str, objectives: List[str], goal_type: str = "general"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.objectives = [
            {
                'description': obj,
                'completed': False,
                'progress': 0.0,
                'metrics': {}
            } for obj in objectives
        ]
        self.created_at = datetime.now()
        self.type = goal_type
        self.status = "active"
        self.priority = 1
        self.dependencies = []
        self.metrics = {
            'engagement_rate': 0.0,
            'influence_score': 0.0,
            'trend_alignment': 0.0
        }

class GoalSystem:
    def __init__(self, goals: List[Dict]):
        self.goals: Dict[str, Goal] = goals
        self.goal_history: List[Dict] = []
        
    async def create_goal(self, name: str, objectives: List[str], 
                         goal_type: str = "general", priority: int = 1) -> Goal:
        """Create a new goal"""
        goal = Goal(name, objectives, goal_type)
        goal.priority = priority
        self.goals[goal.id] = goal
        return goal
        
    async def update_goal_progress(self, goal_id: str, 
                                 objective_index: int, 
                                 progress: float,
                                 metrics: Dict = None) -> Optional[Goal]:
        """Update progress of a specific objective"""
        if goal_id in self.goals:
            goal = self.goals[goal_id]
            if 0 <= objective_index < len(goal.objectives):
                objective = goal.objectives[objective_index]
                objective['progress'] = progress
                if metrics:
                    objective['metrics'].update(metrics)
                
                # Check if goal is completed
                if all(obj['progress'] >= 1.0 for obj in goal.objectives):
                    await self._complete_goal(goal_id)
                    
                return goal
        return None
        
    async def evaluate_goals(self) -> List[Dict]:
        """Evaluate all active goals and their progress"""
        evaluation = []
        for goal in self.goals.values():
            if goal.status == "active":
                progress = sum(obj['progress'] for obj in goal.objectives) / len(goal.objectives)
                evaluation.append({
                    'goal_id': goal.id,
                    'name': goal.name,
                    'progress': progress,
                    'metrics': goal.metrics,
                    'priority': goal.priority
                })
        return evaluation
        
    async def get_priority_objectives(self) -> List[Dict]:
        """Get current priority objectives across all active goals"""
        priority_objectives = []
        for goal in self.goals.values():
            if goal.status == "active":
                incomplete_objectives = [
                    {
                        'goal_id': goal.id,
                        'goal_name': goal.name,
                        'objective': obj['description'],
                        'progress': obj['progress'],
                        'priority': goal.priority
                    }
                    for obj in goal.objectives
                    if obj['progress'] < 1.0
                ]
                priority_objectives.extend(incomplete_objectives)
                
        return sorted(priority_objectives, 
                     key=lambda x: (x['priority'], 1 - x['progress']), 
                     reverse=True) 