from typing import Dict, List, Optional
import uuid
from datetime import datetime

class Goal:
    def __init__(self, name: str, objectives: List[str]):
        self.id = str(uuid.uuid4())
        self.name = name
        self.objectives = [
            {'description': obj, 'completed': False}
            for obj in objectives
        ]
        self.created_at = datetime.now()
        
class GoalSystem:
    def __init__(self):
        self.goals: List[Goal] = []
        
    async def create_goal(self, name: str, objectives: List[str]) -> Goal:
        goal = Goal(name, objectives)
        self.goals.append(goal)
        return goal
        
    async def update_goal(self, goal_id: str, updates: Dict) -> Optional[Goal]:
        for goal in self.goals:
            if goal.id == goal_id:
                for key, value in updates.items():
                    setattr(goal, key, value)
                return goal
        return None 